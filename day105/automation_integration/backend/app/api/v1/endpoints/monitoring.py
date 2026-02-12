from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.workflow import WorkflowExecution, ExecutionStatus
from app.services.execution_engine import execution_engine

router = APIRouter()

class ExecutionMetrics(BaseModel):
    total_executions: int
    completed: int
    failed: int
    running: int
    pending: int
    average_execution_time: float
    success_rate: float

class SystemHealth(BaseModel):
    status: str
    active_workers: int
    queue_size: int
    active_executions: int

@router.get("/metrics", response_model=ExecutionMetrics)
async def get_execution_metrics(db: AsyncSession = Depends(get_db)):
    """Get execution metrics"""
    # Total executions
    total_result = await db.execute(select(func.count(WorkflowExecution.id)))
    total = total_result.scalar() or 0
    
    # Completed
    completed_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.COMPLETED)
    )
    completed = completed_result.scalar() or 0
    
    # Failed
    failed_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.FAILED)
    )
    failed = failed_result.scalar() or 0
    
    # Running
    running_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.RUNNING)
    )
    running = running_result.scalar() or 0
    
    # Pending
    pending_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.PENDING)
    )
    pending = pending_result.scalar() or 0
    
    # Average execution time
    avg_time_result = await db.execute(
        select(func.avg(WorkflowExecution.execution_time))
        .where(WorkflowExecution.execution_time.isnot(None))
    )
    avg_time = avg_time_result.scalar() or 0.0
    
    # Success rate
    success_rate = (completed / total * 100) if total > 0 else 0.0
    
    return ExecutionMetrics(
        total_executions=total,
        completed=completed,
        failed=failed,
        running=running,
        pending=pending,
        average_execution_time=float(avg_time),
        success_rate=success_rate
    )

@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get system health status"""
    return SystemHealth(
        status="healthy" if execution_engine.running else "stopped",
        active_workers=len(execution_engine.worker_tasks),
        queue_size=execution_engine.execution_queue.qsize(),
        active_executions=len(execution_engine.active_executions)
    )
