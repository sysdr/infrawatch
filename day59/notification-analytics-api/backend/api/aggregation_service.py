from fastapi import APIRouter, Depends, BackgroundTasks
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_config import get_db
from services.aggregator import AggregationService
from pydantic import BaseModel

router = APIRouter(prefix="/api/aggregation", tags=["aggregation"])

class AggregationJobResponse(BaseModel):
    status: str
    message: str
    time_bucket: datetime

@router.post("/hourly")
async def trigger_hourly_aggregation(
    time_bucket: datetime,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger hourly aggregation job"""
    
    async def aggregate():
        aggregator = AggregationService(db)
        await aggregator.aggregate_hourly_metrics(time_bucket)
    
    background_tasks.add_task(aggregate)
    
    return AggregationJobResponse(
        status="scheduled",
        message=f"Hourly aggregation scheduled for {time_bucket}",
        time_bucket=time_bucket
    )

@router.post("/daily")
async def trigger_daily_aggregation(
    date: datetime,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger daily aggregation job"""
    
    async def aggregate():
        aggregator = AggregationService(db)
        await aggregator.aggregate_daily_metrics(date)
    
    background_tasks.add_task(aggregate)
    
    return AggregationJobResponse(
        status="scheduled",
        message=f"Daily aggregation scheduled for {date}",
        time_bucket=date
    )

@router.get("/status")
async def get_aggregation_status(db: AsyncSession = Depends(get_db)):
    """Get aggregation job status"""
    from models.analytics_models import NotificationMetricHourly
    from sqlalchemy import select, func
    
    # Get latest aggregated time bucket
    query = select(func.max(NotificationMetricHourly.time_bucket))
    result = await db.execute(query)
    latest = result.scalar()
    
    return {
        "latest_hourly_aggregation": latest,
        "lag_minutes": (datetime.utcnow() - latest).total_seconds() / 60 if latest else None,
        "status": "healthy" if latest and (datetime.utcnow() - latest).total_seconds() < 7200 else "delayed"
    }
