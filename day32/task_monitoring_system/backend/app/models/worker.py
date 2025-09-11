from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

Base = declarative_base()

class WorkerModel(Base):
    __tablename__ = "workers"
    
    id = Column(String(100), primary_key=True)
    name = Column(String(255))
    status = Column(String(50), default="active")
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    task_count = Column(Integer, default=0)
    queue_names = Column(Text)  # JSON array as string
    version = Column(String(50))
    host = Column(String(255))
    port = Column(Integer)
    is_healthy = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WorkerHealthCheck(BaseModel):
    worker_id: str
    cpu_usage: float
    memory_usage: float
    task_count: int
    is_healthy: bool = True

class WorkerResponse(BaseModel):
    id: str
    name: str
    status: str
    last_heartbeat: datetime
    cpu_usage: float
    memory_usage: float
    task_count: int
    is_healthy: bool
    host: str
    port: Optional[int]
    
    class Config:
        from_attributes = True
