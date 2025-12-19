from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

from app.core.redis_client import redis_client
from app.services.data_generator import data_generator

router = APIRouter()

@router.get("/widgets")
async def get_dashboard_widgets(
    count: int = Query(default=50, ge=1, le=1000),
    cache: bool = Query(default=True)
):
    """Get dashboard widgets with caching"""
    cache_key = f"widgets:{count}"
    
    if cache:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return {
                "widgets": cached_data,
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }
    
    # Generate widgets
    widgets = []
    chart_types = ["line", "bar", "scatter", "pie"]
    
    for i in range(count):
        widgets.append({
            "id": f"widget_{i}",
            "type": random.choice(chart_types),
            "title": f"Metric {i+1}",
            "metric": random.choice(data_generator.metric_names),
            "position": {"x": (i % 6) * 300, "y": (i // 6) * 400}
        })
    
    # Cache for 5 minutes
    await redis_client.set(cache_key, widgets, ttl=300)
    
    return {
        "widgets": widgets,
        "cached": False,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/data/{widget_id}")
async def get_widget_data(
    widget_id: str,
    time_range: str = Query(default="1h"),
    resolution: int = Query(default=100, ge=10, le=1920)
):
    """Get optimized chart data for a widget"""
    cache_key = f"widget_data:{widget_id}:{time_range}:{resolution}"
    
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        cached_data["cached"] = True
        return cached_data
    
    # Determine chart type from widget_id or default to line
    chart_type = "line"
    
    # Generate data
    chart_data = data_generator.generate_chart_data(chart_type, resolution)
    
    # Cache for 1 minute
    await redis_client.set(cache_key, chart_data, ttl=60)
    
    chart_data["cached"] = False
    return chart_data
