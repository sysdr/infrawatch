from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ActionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    VALIDATING = "validating"
    DRY_RUN = "dry_run"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionTemplate(Base):
    __tablename__ = "action_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    risk_level = Column(Enum(RiskLevel))
    script_name = Column(String)
    parameters_schema = Column(JSON)
    requires_approval = Column(Boolean, default=False)
    max_blast_radius = Column(Integer, default=100)
    can_rollback = Column(Boolean, default=True)
    rollback_script = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RemediationAction(Base):
    __tablename__ = "remediation_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("action_templates.id"))
    incident_id = Column(String, index=True)
    status = Column(Enum(ActionStatus), default=ActionStatus.PENDING, index=True)
    parameters = Column(JSON)
    risk_score = Column(Float)
    blast_radius = Column(Integer, default=0)
    dry_run_result = Column(JSON, nullable=True)
    execution_result = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_by = Column(String, default="system")
    approved_by = Column(String, nullable=True)
    executed_by = Column(String, default="system")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    approved_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    template = relationship("ActionTemplate")
    approvals = relationship("ApprovalRequest", back_populates="action")
    rollback_data = relationship("RollbackData", back_populates="action", uselist=False)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("remediation_actions.id"))
    approver = Column(String)
    status = Column(String, default="pending")
    comments = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    
    action = relationship("RemediationAction", back_populates="approvals")

class RollbackData(Base):
    __tablename__ = "rollback_data"
    
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("remediation_actions.id"), unique=True)
    state_snapshot = Column(JSON)
    rollback_parameters = Column(JSON)
    expires_at = Column(DateTime)
    rolled_back = Column(Boolean, default=False)
    rolled_back_at = Column(DateTime, nullable=True)
    
    action = relationship("RemediationAction", back_populates="rollback_data")
