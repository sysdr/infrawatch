from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.models.metrics import MetricData
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

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

@router.get("/hierarchy")
async def get_drilldown_hierarchy():
    """Get the drilldown hierarchy structure"""
    return {
        'hierarchy': [
            {'level': 0, 'dimension': 'service', 'label': 'Service'},
            {'level': 1, 'dimension': 'endpoint', 'label': 'Endpoint'},
            {'level': 2, 'dimension': 'region', 'label': 'Region'},
            {'level': 3, 'dimension': 'environment', 'label': 'Environment'},
        ],
        'max_depth': 3
    }

@router.post("/navigate")
async def drilldown_navigate(
    level: int = Query(..., ge=0, le=3),
    context: Dict[str, Any] = None,
    metric_name: str = "latency",
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Navigate drilldown hierarchy"""
    
    if not end_time:
        end_time = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        end_time = normalize_datetime(end_time)
    if not start_time:
        start_time = end_time - timedelta(hours=24)
    else:
        start_time = normalize_datetime(start_time)
    
    context = context or {}
    
    # Determine what to group by based on level
    hierarchy = ['service', 'endpoint', 'region', 'environment']
    current_dimension = hierarchy[level]
    
    # Build conditions from context
    conditions = [
        MetricData.timestamp >= start_time,
        MetricData.timestamp <= end_time,
        MetricData.metric_name == metric_name
    ]
    
    for dim, value in context.items():
        if dim in hierarchy:
            conditions.append(getattr(MetricData, dim) == value)
    
    # Get aggregated data for current level
    column = getattr(MetricData, current_dimension)
    
    query = select(
        column,
        func.avg(MetricData.value).label('avg_value'),
        func.min(MetricData.value).label('min_value'),
        func.max(MetricData.value).label('max_value'),
        func.count(MetricData.id).label('count')
    ).where(
        and_(*conditions)
    ).group_by(
        column
    ).order_by(
        func.avg(MetricData.value).desc()
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return {
        'level': level,
        'dimension': current_dimension,
        'context': context,
        'data': [
            {
                'value': row[0],
                'avg': float(row[1]) if row[1] else 0,
                'min': float(row[2]) if row[2] else 0,
                'max': float(row[3]) if row[3] else 0,
                'count': row[4],
                'drillable': level < 3
            }
            for row in rows
        ],
        'breadcrumbs': _build_breadcrumbs(context, hierarchy[:level+1])
    }

@router.get("/details")
async def get_drilldown_details(
    service: str,
    endpoint: Optional[str] = None,
    region: Optional[str] = None,
    environment: Optional[str] = None,
    metric_name: str = "latency",
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed records for specific drilldown path"""
    
    if not end_time:
        end_time = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        end_time = normalize_datetime(end_time)
    if not start_time:
        start_time = end_time - timedelta(hours=1)
    else:
        start_time = normalize_datetime(start_time)
    
    conditions = [
        MetricData.timestamp >= start_time,
        MetricData.timestamp <= end_time,
        MetricData.service == service,
        MetricData.metric_name == metric_name
    ]
    
    if endpoint:
        conditions.append(MetricData.endpoint == endpoint)
    if region:
        conditions.append(MetricData.region == region)
    if environment:
        conditions.append(MetricData.environment == environment)
    
    query = select(MetricData).where(
        and_(*conditions)
    ).order_by(
        MetricData.timestamp.desc()
    ).limit(limit)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    return {
        'records': [
            {
                'id': m.id,
                'timestamp': m.timestamp.isoformat(),
                'service': m.service,
                'endpoint': m.endpoint,
                'region': m.region,
                'environment': m.environment,
                'value': m.value,
                'status': m.status
            }
            for m in metrics
        ],
        'count': len(metrics),
        'filters': {
            'service': service,
            'endpoint': endpoint,
            'region': region,
            'environment': environment
        }
    }

def _build_breadcrumbs(context: Dict[str, Any], hierarchy: List[str]) -> List[Dict[str, Any]]:
    """Build breadcrumb trail from context"""
    breadcrumbs = [{'label': 'All Services', 'level': -1, 'context': {}}]
    
    current_context = {}
    for level, dim in enumerate(hierarchy):
        if dim in context:
            current_context[dim] = context[dim]
            breadcrumbs.append({
                'label': f"{dim.title()}: {context[dim]}",
                'level': level,
                'context': current_context.copy()
            })
    
    return breadcrumbs
