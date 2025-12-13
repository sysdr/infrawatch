from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.services.chart_service import ChartService

router = APIRouter()
chart_service = ChartService()

@router.get("/multi-series")
async def get_multi_series_data(
    metrics: List[str] = Query(...),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Get multi-series time-series data"""
    if not start_time:
        start_time = datetime.now() - timedelta(hours=24)
    if not end_time:
        end_time = datetime.now()
    
    return chart_service.generate_multi_series(metrics, start_time, end_time)

@router.get("/stacked")
async def get_stacked_data(
    categories: List[str] = Query(...),
    series: List[str] = Query(...)
):
    """Get stacked bar/area chart data"""
    return chart_service.generate_stacked_data(categories, series)

@router.get("/scatter")
async def get_scatter_data(
    x_metric: str,
    y_metric: str,
    samples: int = 1000
):
    """Get scatter plot data showing correlation"""
    return chart_service.generate_scatter_data(x_metric, y_metric, samples)

@router.get("/heatmap")
async def get_heatmap_data(
    metric: str,
    days: int = 7
):
    """Get heatmap data bucketed by hour and day"""
    return chart_service.generate_heatmap_data(metric, days)

@router.get("/custom/latency-distribution")
async def get_latency_distribution():
    """Get latency distribution data for custom chart"""
    return chart_service.generate_latency_distribution()

@router.get("/custom/status-timeline")
async def get_status_timeline(hours: int = 24):
    """Get service status timeline"""
    return chart_service.generate_status_timeline(hours)
