from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from models.k8s_models import ClusterHealth
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/current")
async def get_current_health(db: AsyncSession = Depends(get_db)):
    """Get current cluster health"""
    query = select(ClusterHealth).order_by(desc(ClusterHealth.timestamp)).limit(1)
    result = await db.execute(query)
    health = result.scalar_one_or_none()
    
    if not health:
        return {"status": "unknown", "message": "No health data available"}
    
    return {
        "overall_score": health.overall_score,
        "node_health_score": health.node_health_score,
        "pod_health_score": health.pod_health_score,
        "resource_health_score": health.resource_health_score,
        "deployment_health_score": health.deployment_health_score,
        "api_latency_score": health.api_latency_score,
        "stats": {
            "total_nodes": health.total_nodes,
            "ready_nodes": health.ready_nodes,
            "total_pods": health.total_pods,
            "running_pods": health.running_pods,
            "failed_pods": health.failed_pods,
            "pending_pods": health.pending_pods
        },
        "timestamp": health.timestamp.isoformat()
    }

@router.get("/history")
async def get_health_history(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get health history for specified hours"""
    since = datetime.utcnow() - timedelta(hours=hours)
    query = select(ClusterHealth).where(
        ClusterHealth.timestamp >= since
    ).order_by(ClusterHealth.timestamp)
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    return [
        {
            "timestamp": h.timestamp.isoformat(),
            "overall_score": h.overall_score,
            "node_health": h.node_health_score,
            "pod_health": h.pod_health_score
        }
        for h in history
    ]
