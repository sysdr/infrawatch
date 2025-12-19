from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import List
import random

from app.services.data_generator import data_generator
from app.core.redis_client import redis_client

router = APIRouter()

@router.get("/timeseries")
async def get_time_series(
    metric: str = Query(default="cpu_usage"),
    points: int = Query(default=100, ge=10, le=10000),
    downsample: bool = Query(default=True)
):
    """Get time-series data with automatic downsampling"""
    cache_key = f"timeseries:{metric}:{points}"
    
    cached = await redis_client.get(cache_key)
    if cached:
        return cached
    
    # Generate full resolution data
    data = data_generator.generate_time_series(points, metric)
    
    # Downsample if requested and needed
    max_points = 1920  # Screen width
    if downsample and len(data) > max_points:
        data = data_generator.downsample_lttb(data, max_points)
    
    result = {
        "metric": metric,
        "data": data,
        "original_points": points,
        "returned_points": len(data),
        "downsampled": len(data) < points
    }
    
    await redis_client.set(cache_key, result, ttl=60)
    return result

@router.get("/aggregate")
async def get_aggregated_metrics(
    metrics: str = Query(default="cpu_usage,memory_usage"),
    interval: str = Query(default="5m")
):
    """Get pre-aggregated metrics"""
    metric_list = metrics.split(",")
    
    results = {}
    for metric in metric_list:
        # In production, this would query pre-aggregated data
        results[metric] = {
            "avg": round(random.uniform(30, 70), 2),
            "min": round(random.uniform(10, 30), 2),
            "max": round(random.uniform(70, 95), 2),
            "p95": round(random.uniform(75, 90), 2),
            "p99": round(random.uniform(85, 98), 2)
        }
    
    return {
        "interval": interval,
        "metrics": results,
        "timestamp": datetime.now().isoformat()
    }
