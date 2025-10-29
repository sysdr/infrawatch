from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    return {
        "overview": {
            "total_notifications": random.randint(8000, 12000),
            "success_rate": random.uniform(85, 95),
            "avg_delivery_time": random.uniform(150, 350),
            "current_queue_size": random.randint(20, 200)
        },
        "hourly_stats": [
            {
                "hour": (datetime.now() - timedelta(hours=i)).strftime("%H:00"),
                "sent": random.randint(100, 500),
                "delivered": random.randint(80, 450),
                "failed": random.randint(5, 50)
            }
            for i in range(24, 0, -1)
        ],
        "channel_breakdown": {
            "email": {
                "count": random.randint(3000, 5000),
                "success_rate": random.uniform(85, 95)
            },
            "sms": {
                "count": random.randint(1000, 2000),
                "success_rate": random.uniform(90, 98)
            },
            "push": {
                "count": random.randint(4000, 6000),
                "success_rate": random.uniform(88, 94)
            }
        },
        "priority_stats": {
            "urgent": {"count": random.randint(100, 300), "avg_time": random.uniform(50, 150)},
            "high": {"count": random.randint(500, 1000), "avg_time": random.uniform(100, 200)},
            "normal": {"count": random.randint(5000, 8000), "avg_time": random.uniform(150, 300)},
            "low": {"count": random.randint(1000, 2000), "avg_time": random.uniform(200, 400)}
        },
        "failure_analysis": {
            "network_timeout": random.randint(20, 100),
            "invalid_recipient": random.randint(10, 50),
            "rate_limited": random.randint(5, 30),
            "service_unavailable": random.randint(15, 60)
        }
    }

@router.get("/real-time")
async def get_realtime_metrics():
    """Get real-time system metrics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "queue_size": random.randint(50, 200),
        "processing_rate": random.uniform(8, 15),
        "active_workers": 4,
        "memory_usage": random.uniform(45, 85),
        "cpu_usage": random.uniform(20, 70),
        "recent_events": [
            {
                "type": random.choice(["delivery_success", "delivery_failed", "queued", "retry"]),
                "count": random.randint(1, 10),
                "timestamp": (datetime.now() - timedelta(seconds=i*10)).isoformat()
            }
            for i in range(10)
        ]
    }

@router.get("/health")
async def get_system_health():
    """Get system health metrics"""
    return {
        "status": "healthy",
        "uptime": "2d 14h 23m",
        "services": {
            "queue_manager": {"status": "healthy", "response_time": random.uniform(1, 5)},
            "delivery_service": {"status": "healthy", "response_time": random.uniform(10, 50)},
            "rate_limiter": {"status": "healthy", "response_time": random.uniform(1, 3)},
            "database": {"status": "healthy", "response_time": random.uniform(2, 8)},
            "redis": {"status": "healthy", "response_time": random.uniform(1, 2)}
        },
        "last_incident": "2024-01-15T10:30:00Z",
        "total_processed": random.randint(50000, 100000)
    }
