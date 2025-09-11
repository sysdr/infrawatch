from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class TaskStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.QUEUED)
    worker_id = Column(String(100))
    queue_name = Column(String(100), default="default")
    priority = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    execution_time = Column(Float)
    error_message = Column(Text)
    payload = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TaskCreate(BaseModel):
    name: str
    payload: Dict[str, Any] = {}
    queue_name: str = "default"
    priority: int = 0
    max_retries: int = 3

class TaskResponse(BaseModel):
    id: int
    name: str
    status: TaskStatus
    worker_id: Optional[str]
    queue_name: str
    priority: int
    retry_count: int
    max_retries: int
    execution_time: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
