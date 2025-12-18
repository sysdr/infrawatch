from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, and_
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.metrics import MetricData
from datetime import datetime, timedelta
from typing import Optional, List

router = APIRouter()

@router.get("/available")
async def get_available_filters(
    service: Optional[str] = None,
    endpoint: Optional[str] = None,
    region: Optional[str] = None,
    environment: Optional[str] = None,
    metric_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get available filter values based on current selections (progressive filtering)"""
    
    try:
        cache_key = f"filters:available:{service}:{endpoint}:{region}:{environment}:{metric_name}"
        cached = await redis_client.get(cache_key)
        if cached:
            return cached
        
        # Build base conditions from already selected filters
        conditions = []
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
        
        base_where = and_(*conditions) if conditions else True
        
        # Get distinct values for each dimension
        async def get_distinct_values(column):
            try:
                query = select(distinct(column)).where(base_where).order_by(column)
                result = await db.execute(query)
                # Filter out None/NULL values
                return [row[0] for row in result.all() if row[0] is not None]
            except Exception as e:
                # Return empty list on error instead of crashing
                print(f"Error getting distinct values for {column}: {e}")
                return []
        
        filters = {
            'services': await get_distinct_values(MetricData.service) if not service else [service],
            'endpoints': await get_distinct_values(MetricData.endpoint) if not endpoint else [endpoint],
            'regions': await get_distinct_values(MetricData.region) if not region else [region],
            'environments': await get_distinct_values(MetricData.environment) if not environment else [environment],
            'metrics': await get_distinct_values(MetricData.metric_name) if not metric_name else [metric_name],
            'statuses': await get_distinct_values(MetricData.status)
        }
        
        # Cache for 5 minutes
        await redis_client.set(cache_key, filters, ttl=300)
        
        return filters
    except Exception as e:
        # Return empty filters on any error
        print(f"Error in get_available_filters: {e}")
        return {
            'services': [],
            'endpoints': [],
            'regions': [],
            'environments': [],
            'metrics': [],
            'statuses': []
        }

@router.get("/counts")
async def get_filter_counts(
    dimension: str = Query(..., regex="^(service|endpoint|region|environment|metric_name|status)$"),
    service: Optional[str] = None,
    endpoint: Optional[str] = None,
    region: Optional[str] = None,
    environment: Optional[str] = None,
    metric_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get counts for each filter value"""
    
    conditions = []
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
    
    column = getattr(MetricData, dimension)
    
    query = select(
        column,
        func.count(MetricData.id).label('count')
    ).where(
        and_(*conditions) if conditions else True
    ).group_by(
        column
    ).order_by(
        func.count(MetricData.id).desc()
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return {
        'dimension': dimension,
        'counts': [
            {'value': row[0], 'count': row[1]}
            for row in rows
        ]
    }
