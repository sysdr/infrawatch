from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import json
import time
from ..models.task import TaskModel, TaskCreate, TaskResponse, TaskStatus
from ..utils.database import get_db
from ..utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = TaskModel(
        name=task_data.name,
        payload=json.dumps(task_data.payload),
        queue_name=task_data.queue_name,
        priority=task_data.priority,
        max_retries=task_data.max_retries,
        status=TaskStatus.QUEUED
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    logger.info(f"Task created: {db_task.id}")
    return db_task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task by ID"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    queue_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List tasks with optional filtering"""
    query = db.query(TaskModel)
    
    if status:
        query = query.filter(TaskModel.status == status)
    if queue_name:
        query = query.filter(TaskModel.queue_name == queue_name)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.post("/{task_id}/process")
async def process_task(task_id: int, worker_id: str, db: Session = Depends(get_db)):
    """Mark task as processing and simulate execution"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.QUEUED:
        raise HTTPException(status_code=400, detail="Task not in queued status")
    
    # Update task status
    task.status = TaskStatus.PROCESSING
    task.worker_id = worker_id
    task.started_at = datetime.utcnow()
    db.commit()
    
    # Simulate task processing in background
    async def execute_task():
        try:
            # Simulate work
            execution_time = time.time()
            await asyncio.sleep(2)  # Simulate 2 second task
            execution_time = time.time() - execution_time
            
            # Simulate random failure (10% chance)
            import random
            if random.random() < 0.1:
                raise Exception("Simulated task failure")
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.execution_time = execution_time
            db.commit()
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            # Mark as failed
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                logger.info(f"Task {task_id} failed, retrying ({task.retry_count}/{task.max_retries})")
                # In production, reschedule the task
            else:
                logger.error(f"Task {task_id} failed permanently: {e}")
            
            db.commit()
    
    asyncio.create_task(execute_task())
    return {"message": "Task processing started", "task_id": task_id}

@router.post("/{task_id}/cancel")
async def cancel_task(task_id: int, db: Session = Depends(get_db)):
    """Cancel a task"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    
    task.status = TaskStatus.CANCELLED
    task.completed_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Task {task_id} cancelled")
    return {"message": "Task cancelled", "task_id": task_id}
