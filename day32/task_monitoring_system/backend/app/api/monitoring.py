from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
from ..utils.database import get_db
from ..models.task import TaskModel, TaskStatus
from ..models.worker import WorkerModel
from ..services.monitoring_service import MonitoringService

router = APIRouter()
monitoring_service = MonitoringService()

@router.get("/metrics")
async def get_metrics():
    """Get current system metrics"""
    return await monitoring_service.get_realtime_metrics()

@router.get("/health")
async def health_check():
    """System health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/tasks/stats")
async def get_task_statistics(db: Session = Depends(get_db)):
    """Get task statistics"""
    stats = {}
    
    # Status distribution
    for status in TaskStatus:
        count = db.query(TaskModel).filter(TaskModel.status == status).count()
        stats[status.value] = count
    
    # Performance metrics
    recent_completed = db.query(TaskModel).filter(
        TaskModel.status == TaskStatus.COMPLETED,
        TaskModel.completed_at >= datetime.utcnow() - timedelta(hours=24)
    ).all()
    
    execution_times = [t.execution_time for t in recent_completed if t.execution_time]
    
    if execution_times:
        stats['performance'] = {
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'completed_24h': len(recent_completed)
        }
    
    return stats

@router.get("/workers/health")
async def get_worker_health(db: Session = Depends(get_db)):
    """Get worker health status"""
    workers = db.query(WorkerModel).all()
    
    healthy_workers = [w for w in workers if w.is_healthy]
    unhealthy_workers = [w for w in workers if not w.is_healthy]
    
    return {
        "total_workers": len(workers),
        "healthy_workers": len(healthy_workers),
        "unhealthy_workers": len(unhealthy_workers),
        "workers": [
            {
                "id": w.id,
                "name": w.name,
                "status": w.status,
                "cpu_usage": w.cpu_usage,
                "memory_usage": w.memory_usage,
                "task_count": w.task_count,
                "is_healthy": w.is_healthy,
                "last_heartbeat": w.last_heartbeat
            } for w in workers
        ]
    }

@router.get("/queues/status")
async def get_queue_status(db: Session = Depends(get_db)):
    """Get queue status information"""
    from sqlalchemy import func
    
    queue_stats = db.query(
        TaskModel.queue_name,
        TaskModel.status,
        func.count(TaskModel.id).label('count')
    ).group_by(
        TaskModel.queue_name,
        TaskModel.status
    ).all()
    
    # Organize by queue
    queues = {}
    for queue_name, status, count in queue_stats:
        if queue_name not in queues:
            queues[queue_name] = {}
        queues[queue_name][status.value] = count
    
    return {"queues": queues}
