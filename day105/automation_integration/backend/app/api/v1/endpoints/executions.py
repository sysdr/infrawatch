from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.workflow import WorkflowExecution, ExecutionStep, ExecutionLog, ExecutionStatus
from app.services.execution_engine import execution_engine

router = APIRouter()

class ExecutionCreate(BaseModel):
    workflow_id: int
    input_data: Optional[dict] = None

class ExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    status: str
    input_data: Optional[dict]
    output_data: Optional[dict]
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExecutionStepResponse(BaseModel):
    id: int
    step_name: str
    step_type: str
    status: str
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    
    class Config:
        from_attributes = True

class ExecutionLogResponse(BaseModel):
    id: int
    level: str
    message: str
    step_name: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ExecutionResponse)
async def create_execution(
    execution: ExecutionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create and start a new workflow execution"""
    db_execution = WorkflowExecution(
        workflow_id=execution.workflow_id,
        input_data=execution.input_data,
        status=ExecutionStatus.PENDING
    )
    db.add(db_execution)
    await db.commit()
    await db.refresh(db_execution)
    
    # Submit to execution engine
    await execution_engine.submit_execution(db_execution.id)
    
    return db_execution

@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List workflow executions with optional status filter"""
    query = select(WorkflowExecution).order_by(WorkflowExecution.created_at.desc())
    
    if status:
        query = query.where(WorkflowExecution.status == status)
    
    result = await db.execute(query)
    executions = result.scalars().all()
    return executions

@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get execution by ID"""
    result = await db.execute(
        select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution

@router.get("/{execution_id}/steps", response_model=List[ExecutionStepResponse])
async def get_execution_steps(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get steps for an execution"""
    result = await db.execute(
        select(ExecutionStep)
        .where(ExecutionStep.execution_id == execution_id)
        .order_by(ExecutionStep.id)
    )
    steps = result.scalars().all()
    return steps

@router.get("/{execution_id}/logs", response_model=List[ExecutionLogResponse])
async def get_execution_logs(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get logs for an execution"""
    result = await db.execute(
        select(ExecutionLog)
        .where(ExecutionLog.execution_id == execution_id)
        .order_by(ExecutionLog.timestamp)
    )
    logs = result.scalars().all()
    return logs

@router.post("/{execution_id}/retry")
async def retry_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Retry a failed execution"""
    result = await db.execute(
        select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status not in [ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Only failed or cancelled executions can be retried")
    
    # Reset execution
    execution.status = ExecutionStatus.PENDING
    execution.error_message = None
    execution.retry_count += 1
    
    await db.commit()
    
    # Submit to execution engine
    await execution_engine.submit_execution(execution_id)
    
    return {"message": "Execution retry submitted", "execution_id": execution_id}
