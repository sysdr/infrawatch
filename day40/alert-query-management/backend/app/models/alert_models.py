from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
from .database import Base
from enum import Enum

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default=AlertStatus.ACTIVE, index=True)
    source = Column(String(100), nullable=False, index=True)
    service = Column(String(100), index=True)
    environment = Column(String(50), index=True)
    tags = Column(JSON, default=list)
    alert_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(String(100))

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    condition = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
