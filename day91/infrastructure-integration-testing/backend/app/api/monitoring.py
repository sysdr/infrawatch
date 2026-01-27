"""Monitoring integration API endpoints"""
from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/metrics", response_model=Dict)
async def get_metrics():
    """Get current monitoring metrics"""
    return {
        "total_metrics": 15420,
        "metrics_per_second": 850,
        "active_alerts": 3,
        "monitoring_latency_ms": 28,
        "data_points_24h": 1250000
    }

@router.get("/alerts", response_model=List[Dict])
async def get_active_alerts():
    """Get active monitoring alerts"""
    return [
        {
            "id": "alert-1",
            "resource": "resource-15",
            "type": "cpu_high",
            "severity": "warning",
            "value": 85.5,
            "threshold": 80.0,
            "triggered_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        },
        {
            "id": "alert-2",
            "resource": "resource-8",
            "type": "memory_high",
            "severity": "critical",
            "value": 94.2,
            "threshold": 90.0,
            "triggered_at": (datetime.utcnow() - timedelta(minutes=12)).isoformat()
        }
    ]
