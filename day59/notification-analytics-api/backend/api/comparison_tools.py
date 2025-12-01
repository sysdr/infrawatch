from fastapi import APIRouter, Depends, Query
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_config import get_db
from services.aggregator import AggregationService
from pydantic import BaseModel

router = APIRouter(prefix="/api/analytics", tags=["comparison"])

class ComparisonResponse(BaseModel):
    metric: str
    comparisons: Dict
    summary: Dict

@router.get("/compare")
async def compare_metrics(
    metric: str = Query(..., description="Metric to compare"),
    dimensions: str = Query(..., description="Comma-separated dimension:value pairs"),
    days: int = Query(7, description="Number of days to compare"),
    db: AsyncSession = Depends(get_db)
):
    """Compare metric across different dimensions"""
    
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    
    # Parse dimensions (e.g., "channel:email,channel:sms")
    dimension_pairs = []
    for dim in dimensions.split(','):
        key, value = dim.split(':')
        dimension_pairs.append((key.strip(), value.strip()))
    
    aggregator = AggregationService(db)
    
    # Query each dimension
    results = {}
    for dim_key, dim_value in dimension_pairs:
        data = await aggregator.query_metrics(
            metric=metric,
            group_by=['time'],
            start=start,
            end=end,
            filters={dim_key: dim_value}
        )
        
        if data:
            total_value = sum(d['value'] for d in data)
            avg_value = total_value / len(data)
            results[dim_value] = {
                "total": total_value,
                "average": avg_value,
                "data_points": len(data),
                "latest": data[-1]['value'] if data else 0
            }
    
    # Calculate comparisons
    summary = {}
    if len(results) >= 2:
        values = list(results.values())
        summary = {
            "highest": max(results.keys(), key=lambda k: results[k]['average']),
            "lowest": min(results.keys(), key=lambda k: results[k]['average']),
            "average_difference": abs(values[0]['average'] - values[1]['average']),
            "percent_difference": (
                abs(values[0]['average'] - values[1]['average']) / 
                max(values[0]['average'], values[1]['average']) * 100
            ) if max(values[0]['average'], values[1]['average']) > 0 else 0
        }
    
    return ComparisonResponse(
        metric=metric,
        comparisons=results,
        summary=summary
    )

@router.get("/compare/channels")
async def compare_channels(
    metric: str,
    channels: str = Query("email,sms,push", description="Channels to compare"),
    days: int = Query(7),
    db: AsyncSession = Depends(get_db)
):
    """Compare metric across channels"""
    
    dimensions = ','.join([f"channel:{c.strip()}" for c in channels.split(',')])
    return await compare_metrics(metric, dimensions, days, db)

@router.get("/drilldown")
async def drill_down(
    level: int = Query(0, description="Drill-down level (0=top)"),
    dimension: str = Query("channel", description="Dimension to drill into"),
    parent_filters: str = Query("", description="JSON string of parent filters"),
    days: int = Query(7),
    db: AsyncSession = Depends(get_db)
):
    """Drill down from summary to detailed metrics"""
    
    import json
    
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    
    # Parse parent filters
    filters = json.loads(parent_filters) if parent_filters else {}
    
    aggregator = AggregationService(db)
    
    # Query with current dimension
    data = await aggregator.query_metrics(
        metric='event_count',
        group_by=[dimension],
        start=start,
        end=end,
        filters=filters if filters else None
    )
    
    # Determine next available dimensions
    next_dimensions = get_next_dimensions(level, dimension)
    
    return {
        "level": level,
        "dimension": dimension,
        "parent_filters": filters,
        "data": data,
        "next_dimensions": next_dimensions,
        "can_drill_down": len(next_dimensions) > 0
    }

def get_next_dimensions(level: int, current_dim: str) -> List[str]:
    """Get available dimensions for next drill-down level"""
    hierarchy = ['channel', 'status', 'template_id']
    
    try:
        current_index = hierarchy.index(current_dim)
        return hierarchy[current_index + 1:]
    except (ValueError, IndexError):
        return []
