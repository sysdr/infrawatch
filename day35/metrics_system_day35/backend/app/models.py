from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
from datetime import datetime
import uuid

Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"

class TaskPriority(enum.Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 9

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(String(100), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL)
    payload = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    celery_id = Column(String, nullable=True, index=True)
    worker_id = Column(String, nullable=True)
    execution_time = Column(Float, nullable=True)
    
class TaskResult(Base):
    __tablename__ = "task_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, nullable=False, index=True)
    result_data = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    tags = Column(JSON, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
