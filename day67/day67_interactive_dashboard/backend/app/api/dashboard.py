from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.metrics import MetricData
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import hashlib
import json

def normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize datetime to UTC timezone-aware"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Naive datetime, assume UTC
        return dt.replace(tzinfo=timezone.utc)
    # Timezone-aware, convert to UTC
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    service: Optional[str] = None,
    endpoint: Optional[str] = None,
    region: Optional[str] = None,
    environment: Optional[str] = None,
    metric_name: Optional[str] = None,
    status: Optional[str] = None,
    zoom_min: Optional[float] = None,
    zoom_max: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard metrics with optional filters and zoom"""
    
    try:
        # Default time range: last 24 hours
        if not end_time:
            end_time = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            end_time = normalize_datetime(end_time)
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        else:
            start_time = normalize_datetime(start_time)
        
        # Create cache key from all parameters
        cache_key = _create_cache_key({
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'service': service,
            'endpoint': endpoint,
            'region': region,
            'environment': environment,
            'metric_name': metric_name,
            'status': status,
            'zoom_min': zoom_min,
            'zoom_max': zoom_max
        })
        
        # Try to get from cache
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        # Build query with filters
        conditions = [
            MetricData.timestamp >= start_time,
            MetricData.timestamp <= end_time
        ]
        
        if service:
            conditions.append(MetricData.service == service)
        if endpoint:
            conditions.append(MetricData.endpoint == endpoint)
        if region:
            conditions.append(MetricData.region == region)
        if environment:
            conditions.append(MetricData.environment == environment)
        if metric_name:
            conditions.append(MetricData.metric_name == metric_name)
        if status:
            conditions.append(MetricData.status == status)
        if zoom_min is not None:
            conditions.append(MetricData.value >= zoom_min)
        if zoom_max is not None:
            conditions.append(MetricData.value <= zoom_max)
        
        # Execute query
        query = select(MetricData).where(and_(*conditions)).order_by(MetricData.timestamp)
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        # Format response
        response_data = {
            'metrics': [
                {
                    'id': m.id,
                    'timestamp': m.timestamp.isoformat(),
                    'service': m.service,
                    'endpoint': m.endpoint,
                    'region': m.region,
                    'environment': m.environment,
                    'metric_name': m.metric_name,
                    'value': m.value,
                    'status': m.status
                }
                for m in metrics
            ],
            'count': len(metrics),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            }
        }
        
        # Cache the result
        await redis_client.set(cache_key, response_data, ttl=300)  # 5 minutes
        
        return response_data
    except Exception as e:
        print(f"Error in get_dashboard_metrics: {e}")
        return {
            'metrics': [],
            'count': 0,
            'time_range': {
                'start': start_time.isoformat() if start_time else datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                'end': end_time.isoformat() if end_time else datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            }
        }

@router.get("/aggregated")
async def get_aggregated_metrics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    group_by: str = Query("service", regex="^(service|endpoint|region|environment|metric_name)$"),
    metric_name: str = "latency",
    aggregation: str = Query("avg", regex="^(avg|sum|min|max|count)$"),
    service: Optional[str] = None,
    region: Optional[str] = None,
    environment: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated metrics for charts"""
    
    try:
        if not end_time:
            end_time = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            end_time = normalize_datetime(end_time)
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        else:
            start_time = normalize_datetime(start_time)
        
        # Build conditions
        conditions = [
            MetricData.timestamp >= start_time,
            MetricData.timestamp <= end_time,
            MetricData.metric_name == metric_name
        ]
        
        if service:
            conditions.append(MetricData.service == service)
        if region:
            conditions.append(MetricData.region == region)
        if environment:
            conditions.append(MetricData.environment == environment)
        
        # Select aggregation function
        agg_func = {
            'avg': func.avg,
            'sum': func.sum,
            'min': func.min,
            'max': func.max,
            'count': func.count
        }[aggregation]
        
        # Group by column
        group_column = getattr(MetricData, group_by)
        
        # Build aggregation query
        query = select(
            group_column,
            agg_func(MetricData.value).label('value'),
            func.count(MetricData.id).label('count')
        ).where(
            and_(*conditions)
        ).group_by(
            group_column
        ).order_by(
            func.avg(MetricData.value).desc()
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        return {
            'data': [
                {
                    'dimension': row[0],
                    'value': float(row[1]) if row[1] else 0,
                    'count': row[2]
                }
                for row in rows
            ],
            'group_by': group_by,
            'metric': metric_name,
            'aggregation': aggregation
        }
    except Exception as e:
        print(f"Error in get_aggregated_metrics: {e}")
        return {
            'data': [],
            'group_by': group_by,
            'metric': metric_name,
            'aggregation': aggregation
        }

@router.get("/timeseries")
async def get_timeseries_data(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    metric_name: str = "latency",
    interval: str = Query("5m", regex="^(1m|5m|15m|1h|6h|1d)$"),
    service: Optional[str] = None,
    endpoint: Optional[str] = None,
    region: Optional[str] = None,
    environment: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get time series data with bucketing"""
    
    try:
        if not end_time:
            end_time = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            end_time = normalize_datetime(end_time)
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        else:
            start_time = normalize_datetime(start_time)
        
        # Build conditions
        conditions = [
            MetricData.timestamp >= start_time,
            MetricData.timestamp <= end_time,
            MetricData.metric_name == metric_name
        ]
        
        if service:
            conditions.append(MetricData.service == service)
        if endpoint:
            conditions.append(MetricData.endpoint == endpoint)
        if region:
            conditions.append(MetricData.region == region)
        if environment:
            conditions.append(MetricData.environment == environment)
        
        # Query raw data (in production, use time-bucket aggregation)
        query = select(MetricData).where(and_(*conditions)).order_by(MetricData.timestamp)
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        # Manual bucketing (in production, use PostgreSQL generate_series or TimescaleDB)
        interval_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '1h': 60, '6h': 360, '1d': 1440
        }[interval]
        
        buckets = {}
        for metric in metrics:
            bucket_time = metric.timestamp.replace(second=0, microsecond=0)
            bucket_time = bucket_time - timedelta(
                minutes=bucket_time.minute % interval_minutes
            )
            
            bucket_key = bucket_time.isoformat()
            if bucket_key not in buckets:
                buckets[bucket_key] = {'values': [], 'timestamp': bucket_time}
            buckets[bucket_key]['values'].append(metric.value)
        
        # Calculate averages
        timeseries = []
        for bucket_key in sorted(buckets.keys()):
            bucket = buckets[bucket_key]
            values = bucket['values']
            timeseries.append({
                'timestamp': bucket_key,
                'value': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            })
        
        return {
            'data': timeseries,
            'interval': interval,
            'metric': metric_name
        }
    except Exception as e:
        print(f"Error in get_timeseries_data: {e}")
        return {
            'data': [],
            'interval': interval,
            'metric': metric_name
        }

def _create_cache_key(params: Dict[str, Any]) -> str:
    """Create cache key from parameters"""
    params_str = json.dumps(params, sort_keys=True, default=str)
    return f"dashboard:metrics:{hashlib.md5(params_str.encode()).hexdigest()}"
