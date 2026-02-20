from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import json
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import MetricSnapshotCreate, MetricSnapshotOut, CorrelationRequest, CorrelationResponse
from app.services.correlation_service import CorrelationService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    svc = AnalyticsService(db, redis)
    return await svc.get_dashboard()

@router.post("/metrics", response_model=MetricSnapshotOut)
async def create_metric(payload: MetricSnapshotCreate, db: AsyncSession = Depends(get_db)):
    from app.models.analytics import MetricSnapshot
    m = MetricSnapshot(**payload.model_dump())
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m

@router.get("/metrics/{metric_name}")
async def get_metric_series(metric_name: str, hours: int = 6,
                            db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    svc = AnalyticsService(db, redis)
    return await svc.get_metric_series(metric_name, hours)

@router.post("/correlate", response_model=CorrelationResponse)
async def compute_correlation(payload: CorrelationRequest, db: AsyncSession = Depends(get_db)):
    svc = CorrelationService(db)
    return await svc.compute_matrix(payload.metrics, payload.time_window_hours, payload.method)

@router.websocket("/ws")
async def websocket_metrics(websocket: WebSocket, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    await websocket.accept()
    svc = AnalyticsService(db, redis)
    try:
        while True:
            dashboard = await svc.get_dashboard()
            payload = {
                "type": "dashboard_update",
                "data": {
                    "kpis": [k.model_dump() for k in dashboard.kpis],
                    "updated_at": dashboard.updated_at.isoformat(),
                },
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
