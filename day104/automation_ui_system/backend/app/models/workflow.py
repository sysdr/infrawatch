from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base

class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class ExecutionStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    definition = Column(JSON, nullable=False)  # DAG structure
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100))
    
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    scripts = relationship("AutomationScript", back_populates="workflow")

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.QUEUED, index=True)
    trigger_type = Column(String(50))  # manual, scheduled, webhook
    input_params = Column(JSON)
    output_result = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    workflow = relationship("Workflow", back_populates="executions")
    steps = relationship("ExecutionStep", back_populates="execution", cascade="all, delete-orphan")

class ExecutionStep(Base):
    __tablename__ = "execution_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False, index=True)
    step_name = Column(String(255), nullable=False)
    step_type = Column(String(50))
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.QUEUED)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    retry_count = Column(Integer, default=0)
    
    execution = relationship("WorkflowExecution", back_populates="steps")

class AutomationScript(Base):
    __tablename__ = "automation_scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    script_type = Column(String(50))  # python, bash, javascript
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    workflow = relationship("Workflow", back_populates="scripts")

class WorkflowSchedule(Base):
    __tablename__ = "workflow_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    next_run_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
