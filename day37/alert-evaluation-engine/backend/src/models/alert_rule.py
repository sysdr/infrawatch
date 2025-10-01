from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

Base = declarative_base()

class RuleType(str, Enum):
    THRESHOLD = "THRESHOLD"
    ANOMALY = "ANOMALY"
    COMPOSITE = "COMPOSITE"

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AlertState(str, Enum):
    OK = "OK"
    PENDING = "PENDING"
    FIRING = "FIRING"
    RESOLVED = "RESOLVED"

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    metric_name = Column(String, index=True)
    rule_type = Column(SQLEnum(RuleType))
    conditions = Column(JSON)  # Flexible condition storage
    severity = Column(SQLEnum(AlertSeverity))
    evaluation_interval = Column(Integer, default=30)  # seconds
    for_duration = Column(Integer, default=0)  # seconds to wait before firing
    labels = Column(JSON)
    annotations = Column(JSON)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AlertInstance(Base):
    __tablename__ = "alert_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, index=True)
    fingerprint = Column(String, unique=True, index=True)
    state = Column(SQLEnum(AlertState), default=AlertState.OK)
    value = Column(Float)
    labels = Column(JSON)
    annotations = Column(JSON)
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models for API
class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    metric_name: str
    rule_type: RuleType
    conditions: Dict[str, Any]
    severity: AlertSeverity
    evaluation_interval: int = 30
    for_duration: int = 0
    labels: Optional[Dict[str, str]] = {}
    annotations: Optional[Dict[str, str]] = {}
    enabled: bool = True

class AlertRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    metric_name: str
    rule_type: RuleType
    conditions: Dict[str, Any]
    severity: AlertSeverity
    evaluation_interval: int
    for_duration: int
    labels: Dict[str, str]
    annotations: Dict[str, str]
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
