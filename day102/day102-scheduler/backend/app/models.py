from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    command = Column(Text, nullable=False)
    cron_expression = Column(String(100))
    timezone = Column(String(50), default="UTC")
    priority = Column(Integer, default=5)
    resources = Column(JSON, default={"cpu": 1, "memory": 512})
    retry_policy = Column(JSON, default={"max_retries": 0, "backoff_type": "fixed", "backoff_base": 60})
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    schedules = relationship("Schedule", back_populates="job", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="job", cascade="all, delete-orphan")
    upstream_deps = relationship("Dependency", foreign_keys="Dependency.downstream_job_id", back_populates="downstream_job")
    downstream_deps = relationship("Dependency", foreign_keys="Dependency.upstream_job_id", back_populates="upstream_job")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    next_run_time = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), default="UTC")
    enabled = Column(Boolean, default=True)
    
    job = relationship("Job", back_populates="schedules")

class Dependency(Base):
    __tablename__ = "dependencies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    upstream_job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    downstream_job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    condition_type = Column(String(20), default="success")  # success, completion, partial_ok
    
    upstream_job = relationship("Job", foreign_keys=[upstream_job_id], back_populates="downstream_deps")
    downstream_job = relationship("Job", foreign_keys=[downstream_job_id], back_populates="upstream_deps")

class Execution(Base):
    __tablename__ = "executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    state = Column(String(20), default="TRIGGERED", index=True)  # TRIGGERED, PENDING, QUEUED, RUNNING, COMPLETED, FAILED, RETRYING, CANCELLED, TIMEOUT, SKIPPED
    trigger_type = Column(String(20), default="schedule")  # schedule, manual, event, dependency
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    exit_code = Column(Integer)
    worker_id = Column(String(100))
    resource_allocation = Column(JSON)
    logs = Column(Text)
    state_history = Column(JSON, default=[])
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    job = relationship("Job", back_populates="executions")

class ResourcePool(Base):
    __tablename__ = "resource_pools"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_type = Column(String(50), nullable=False, unique=True)
    total_capacity = Column(Float, nullable=False)
    allocated_capacity = Column(Float, default=0)
    queue_size = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
