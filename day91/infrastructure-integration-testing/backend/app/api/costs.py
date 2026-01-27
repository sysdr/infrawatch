"""Cost tracking API endpoints"""
from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/summary", response_model=Dict)
async def get_cost_summary():
    """Get cost tracking summary"""
    return {
        "total_monthly_cost": 45632.50,
        "cost_by_service": {
            "EC2": 28450.00,
            "RDS": 8920.50,
            "S3": 3450.00,
            "Lambda": 2312.00,
            "Other": 2500.00
        },
        "cost_by_region": {
            "us-east-1": 22500.00,
            "us-west-2": 15432.50,
            "eu-west-1": 7700.00
        },
        "tracking_accuracy": 99.5,
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/trends", response_model=List[Dict])
async def get_cost_trends():
    """Get cost trends"""
    trends = []
    for i in range(30):
        trends.append({
            "date": (datetime.utcnow() - timedelta(days=29-i)).date().isoformat(),
            "cost": round(random.uniform(1200, 1800), 2)
        })
    return trends
