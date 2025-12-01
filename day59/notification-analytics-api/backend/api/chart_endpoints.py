from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_config import get_db
from services.aggregator import AggregationService
from services.cache_manager import CacheManager
from pydantic import BaseModel

router = APIRouter(prefix="/api/analytics", tags=["charts"])

class ChartDataRequest(BaseModel):
    metric: str
    group_by: List[str]
    start: datetime
    end: datetime
    filters: Optional[Dict] = None

class ChartDataResponse(BaseModel):
    data: List[Dict]
    metadata: Dict

@router.get("/chart")
async def get_chart_data(
    metric: str = Query(..., description="Metric to visualize"),
    group_by: str = Query(..., description="Comma-separated grouping dimensions"),
    start: datetime = Query(..., description="Start time"),
    end: datetime = Query(..., description="End time"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    status: Optional[str] = Query(None, description="Filter by status"),
    template_id: Optional[int] = Query(None, description="Filter by template"),
    db: AsyncSession = Depends(get_db)
):
    """Get chart data with dynamic grouping and filtering"""
    
    # Parse group_by
    group_by_list = [g.strip() for g in group_by.split(',')]
    
    # Build filters
    filters = {}
    if channel:
        filters['channel'] = channel
    if status:
        filters['status'] = status
    if template_id:
        filters['template_id'] = template_id
    
    # Generate cache key
    cache_key = CacheManager.generate_cache_key(
        "chart",
        metric=metric,
        group_by=group_by_list,
        start=start,
        end=end,
        filters=filters
    )
    
    # Try cache first
    async def compute_data():
        aggregator = AggregationService(db)
        return await aggregator.query_metrics(
            metric, group_by_list, start, end, filters
        )
    
    data = await CacheManager.get_or_compute(cache_key, compute_data, ttl=60)
    
    # Format for chart library
    formatted_data = format_for_chart_type(data, detect_chart_type(group_by_list))
    
    return ChartDataResponse(
        data=formatted_data,
        metadata={
            "metric": metric,
            "group_by": group_by_list,
            "time_range": f"{start} to {end}",
            "total_points": len(formatted_data)
        }
    )

def detect_chart_type(group_by: List[str]) -> str:
    """Detect appropriate chart type from grouping"""
    if 'time' in group_by or any(g in ['hour', 'day', 'week'] for g in group_by):
        return 'line'
    elif len(group_by) == 1:
        return 'bar'
    elif len(group_by) == 2:
        return 'heatmap'
    return 'line'

def format_for_chart_type(data: List[Dict], chart_type: str) -> List[Dict]:
    """Format data for specific chart type"""
    if chart_type == 'line':
        # Recharts line chart format
        return data
    elif chart_type == 'bar':
        # Recharts bar chart format
        return data
    elif chart_type == 'heatmap':
        # Transform to heatmap format
        return data
    return data

@router.get("/chart/timeseries")
async def get_timeseries_chart(
    metric: str,
    channels: str = Query("email,sms,push", description="Comma-separated channels"),
    hours: int = Query(24, description="Number of hours to show"),
    db: AsyncSession = Depends(get_db)
):
    """Get time-series chart data for multiple channels"""
    
    end = datetime.utcnow()
    start = end - timedelta(hours=hours)
    
    channel_list = [c.strip() for c in channels.split(',')]
    
    aggregator = AggregationService(db)
    
    # Query data for each channel
    all_data = []
    for channel in channel_list:
        data = await aggregator.query_metrics(
            metric=metric,
            group_by=['time'],
            start=start,
            end=end,
            filters={'channel': channel}
        )
        
        for point in data:
            point['channel'] = channel
            all_data.append(point)
    
    # Group by time
    time_grouped = {}
    for point in all_data:
        time_key = point['time'].isoformat()
        if time_key not in time_grouped:
            time_grouped[time_key] = {'time': time_key}
        time_grouped[time_key][point['channel']] = point['value']
    
    return {
        "data": list(time_grouped.values()),
        "channels": channel_list,
        "metric": metric
    }
