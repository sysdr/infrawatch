from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..models.worker import WorkerModel, WorkerHealthCheck, WorkerResponse
from ..utils.database import get_db
from ..utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/register")
async def register_worker(
    worker_id: str,
    name: str,
    host: str,
    port: int = None,
    db: Session = Depends(get_db)
):
    """Register a new worker"""
    worker = db.query(WorkerModel).filter(WorkerModel.id == worker_id).first()
    
    if worker:
        # Update existing worker
        worker.name = name
        worker.host = host
        worker.port = port
        worker.status = "active"
        worker.last_heartbeat = datetime.utcnow()
        worker.is_healthy = True
    else:
        # Create new worker
        worker = WorkerModel(
            id=worker_id,
            name=name,
            host=host,
            port=port,
            status="active",
            is_healthy=True
        )
        db.add(worker)
    
    db.commit()
    db.refresh(worker)
    
    logger.info(f"Worker registered: {worker_id}")
    return {"message": "Worker registered successfully"}

@router.post("/{worker_id}/heartbeat")
async def worker_heartbeat(
    worker_id: str,
    health_data: WorkerHealthCheck,
    db: Session = Depends(get_db)
):
    """Receive worker heartbeat with health data"""
    worker = db.query(WorkerModel).filter(WorkerModel.id == worker_id).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Update health data
    worker.last_heartbeat = datetime.utcnow()
    worker.cpu_usage = health_data.cpu_usage
    worker.memory_usage = health_data.memory_usage
    worker.task_count = health_data.task_count
    worker.is_healthy = health_data.is_healthy
    worker.status = "active" if health_data.is_healthy else "unhealthy"
    
    db.commit()
    
    return {"message": "Heartbeat received"}

@router.get("/", response_model=List[WorkerResponse])
async def list_workers(db: Session = Depends(get_db)):
    """List all workers"""
    workers = db.query(WorkerModel).all()
    return workers

@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(worker_id: str, db: Session = Depends(get_db)):
    """Get worker details"""
    worker = db.query(WorkerModel).filter(WorkerModel.id == worker_id).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return worker

@router.delete("/{worker_id}")
async def unregister_worker(worker_id: str, db: Session = Depends(get_db)):
    """Unregister a worker"""
    worker = db.query(WorkerModel).filter(WorkerModel.id == worker_id).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    db.delete(worker)
    db.commit()
    
    logger.info(f"Worker unregistered: {worker_id}")
    return {"message": "Worker unregistered successfully"}
