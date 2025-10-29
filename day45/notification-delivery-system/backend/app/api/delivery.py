from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import random

router = APIRouter()

class DeliveryStats(BaseModel):
    total_sent: int
    successful: int
    failed_temporary: int
    failed_permanent: int
    rate_limited: int
    avg_delivery_time: float
    success_rate: float

# Mock delivery data for demo
delivery_data = {
    "total_sent": 0,
    "successful": 0,
    "failed_temporary": 0,
    "failed_permanent": 0,
    "rate_limited": 0,
    "avg_delivery_time": 0.0
}

@router.get("/stats", response_model=DeliveryStats)
async def get_delivery_stats():
    """Get delivery statistics"""
    # Update with some realistic demo data
    total = max(delivery_data["total_sent"], 100)
    successful = int(total * 0.85)
    failed_temp = int(total * 0.10)
    failed_perm = int(total * 0.03)
    rate_limited = total - successful - failed_temp - failed_perm
    
    success_rate = (successful / total * 100) if total > 0 else 0
    
    return DeliveryStats(
        total_sent=total,
        successful=successful,
        failed_temporary=failed_temp,
        failed_permanent=failed_perm,
        rate_limited=rate_limited,
        avg_delivery_time=random.uniform(150, 350),
        success_rate=success_rate
    )

@router.get("/channels")
async def get_channel_stats():
    """Get delivery stats by channel"""
    return {
        "email": {
            "sent": random.randint(800, 1200),
            "success_rate": random.uniform(85, 95),
            "avg_delivery_time": random.uniform(200, 400)
        },
        "sms": {
            "sent": random.randint(300, 600),
            "success_rate": random.uniform(90, 98),
            "avg_delivery_time": random.uniform(100, 250)
        },
        "push": {
            "sent": random.randint(1000, 2000),
            "success_rate": random.uniform(88, 94),
            "avg_delivery_time": random.uniform(50, 150)
        }
    }

@router.get("/real-time")
async def get_realtime_delivery():
    """Get real-time delivery data"""
    return {
        "current_queue_size": random.randint(50, 200),
        "processing_rate": random.uniform(8, 15),
        "active_workers": 4,
        "recent_deliveries": [
            {
                "id": f"notif_{i}",
                "channel": random.choice(["email", "sms", "push"]),
                "status": random.choice(["delivered", "failed", "retry"]),
                "timestamp": datetime.now().isoformat(),
                "delivery_time": random.uniform(50, 300)
            }
            for i in range(10)
        ]
    }
