from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.core.database import get_db
from models.k8s_models import ResourceMetrics, Pod
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.get("/pod/{namespace}/{pod_name}")
async def get_pod_metrics(
    namespace: str,
    pod_name: str,
    hours: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Get metrics for a specific pod"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(ResourceMetrics).where(
        ResourceMetrics.resource_type == 'pod',
        ResourceMetrics.namespace == namespace,
        ResourceMetrics.resource_name == pod_name,
        ResourceMetrics.timestamp >= since
    ).order_by(ResourceMetrics.timestamp)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    return [
        {
            "timestamp": m.timestamp.isoformat(),
            "cpu_usage": m.cpu_usage,
            "memory_usage": m.memory_usage,
            "cpu_limit": m.cpu_limit,
            "memory_limit": m.memory_limit
        }
        for m in metrics
    ]

@router.get("/summary")
async def get_metrics_summary(db: AsyncSession = Depends(get_db)):
    """Get cluster-wide resource usage summary"""
    # Get pod count by namespace
    query = select(
        Pod.namespace,
        func.count(Pod.id).label('pod_count'),
        func.sum(Pod.restart_count).label('total_restarts')
    ).group_by(Pod.namespace)
    
    result = await db.execute(query)
    namespace_stats = result.all()
    
    return {
        "namespaces": [
            {
                "namespace": stat.namespace,
                "pod_count": stat.pod_count,
                "total_restarts": stat.total_restarts or 0
            }
            for stat in namespace_stats
        ]
    }
