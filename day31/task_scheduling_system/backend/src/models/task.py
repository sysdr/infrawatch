from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    task_function = Column(String(100), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    priority = Column(Integer, default=5)
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=300)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("TaskExecution", back_populates="task")

class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    status = Column(String(50), nullable=False)  # running, completed, failed, cancelled
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    result = Column(Text)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    task = relationship("Task", back_populates="executions")

class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(50), default="idle")  # idle, busy, offline
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    max_concurrent_tasks = Column(Integer, default=5)
    current_tasks = Column(Integer, default=0)
    specializations = Column(JSON, default=[])  # e.g., ["cpu_intensive", "io_intensive"]
