from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database import db_service
from app.services.metrics_service import metrics_service
from app.services.redis_service import redis_service
from app.schemas.metrics import MetricCreate, MetricBatch, MetricQuery, MetricResponse, HealthCheck
from typing import List
import json
import asyncio
import structlog
from datetime import datetime

logger = structlog.get_logger()
router = APIRouter()

# Dependency
async def get_db():
    async for session in db_service.get_session():
        yield session

@router.post("/metrics", response_model=MetricResponse)
async def create_metric(
    metric: MetricCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a single metric entry"""
    try:
        db_metric = await metrics_service.create_metric(db, metric)
        return MetricResponse.from_orm(db_metric)
    except Exception as e:
        logger.error("Failed to create metric", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create metric")

@router.post("/metrics/batch")
async def create_metrics_batch(
    batch: MetricBatch,
    db: AsyncSession = Depends(get_db)
):
    """Create multiple metrics in a batch"""
    try:
        db_metrics = await metrics_service.create_metrics_batch(db, batch.metrics)
        return {"created": len(db_metrics), "status": "success"}
    except Exception as e:
        logger.error("Failed to create metrics batch", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create metrics batch")

@router.get("/metrics", response_model=List[MetricResponse])
async def query_metrics(
    name: str = None,
    source: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Query metrics with filters"""
    query = MetricQuery(
        name=name,
        source=source,
        limit=min(limit, 1000),
        offset=offset
    )
    return await metrics_service.query_metrics(db, query)

@router.get("/metrics/realtime")
async def get_realtime_metrics():
    """Get current metrics from Redis cache"""
    try:
        metrics = await metrics_service.get_realtime_metrics()
        return {"metrics": metrics, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error("Failed to get realtime metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get realtime metrics")

@router.get("/metrics/{name}/summary")
async def get_metric_summary(
    name: str,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get statistical summary for a metric"""
    try:
        summary = await metrics_service.get_metric_summary(db, name, hours)
        return summary
    except Exception as e:
        logger.error("Failed to get metric summary", name=name, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metric summary")

@router.get("/stream")
async def stream_metrics():
    """Server-Sent Events stream for real-time updates"""
    async def event_generator():
        try:
            # Subscribe to Redis pub/sub
            if not redis_service.redis:
                return
                
            pubsub = redis_service.redis.pubsub()
            await pubsub.subscribe("metrics_updates")
            
            yield "data: {\"type\": \"connected\"}\n\n"
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    yield f"data: {data}\n\n"
                    
        except asyncio.CancelledError:
            logger.info("SSE stream cancelled")
        except Exception as e:
            logger.error("SSE stream error", error=str(e))
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """System health check"""
    db_healthy = await db_service.health_check()
    redis_healthy = await redis_service.health_check()
    
    status = "healthy" if db_healthy and redis_healthy else "degraded"
    
    return HealthCheck(
        status=status,
        timestamp=datetime.now(),
        database=db_healthy,
        redis=redis_healthy
    )
