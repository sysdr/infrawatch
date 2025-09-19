from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from ..models import TaskStatus, TaskPriority

class TaskCreate(BaseModel):
    task_type: str
    payload: Optional[Dict[str, Any]] = {}
    priority: TaskPriority = TaskPriority.NORMAL

class TaskResponse(BaseModel):
    id: str
    task_type: str
    status: TaskStatus
    priority: TaskPriority
    payload: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    
    class Config:
        from_attributes = True

class TaskStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    processing_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    avg_execution_time: float
    tasks_per_hour: int
    queue_sizes: Dict[str, int]
