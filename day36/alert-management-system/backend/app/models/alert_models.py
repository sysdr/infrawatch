from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime, timezone
from enum import Enum as PyEnum
from .base import Base

class AlertSeverity(PyEnum):
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertOperator(PyEnum):
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"

class AlertStatus(PyEnum):
    PENDING = "pending"
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    metric_name = Column(String(255), nullable=False)
    threshold_value = Column(Float, nullable=False)
    operator = Column(Enum(AlertOperator), nullable=False)
    evaluation_window = Column(String(50), default="5m")
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    labels = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    alert_instances = relationship("AlertInstance", back_populates="rule")
    escalation_policies = relationship("EscalationPolicy", back_populates="alert_rule")

class AlertInstance(Base):
    __tablename__ = "alert_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    current_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    suppressed_until = Column(DateTime, nullable=True)
    message = Column(Text)
    labels = Column(JSON, default={})
    
    # Relationships
    rule = relationship("AlertRule", back_populates="alert_instances")
    state_history = relationship("AlertState", back_populates="alert_instance")

class AlertState(Base):
    __tablename__ = "alert_states"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_instance_id = Column(Integer, ForeignKey("alert_instances.id"), nullable=False)
    from_status = Column(Enum(AlertStatus), nullable=True)
    to_status = Column(Enum(AlertStatus), nullable=False)
    changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    changed_by = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    
    # Relationships
    alert_instance = relationship("AlertInstance", back_populates="state_history")

class EscalationPolicy(Base):
    __tablename__ = "escalation_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    alert_rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    escalation_level = Column(Integer, default=1)
    delay_minutes = Column(Integer, default=15)
    notification_channels = Column(JSON, default=[])  # ["email", "slack", "pagerduty"]
    recipients = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    alert_rule = relationship("AlertRule", back_populates="escalation_policies")

class SuppressionRule(Base):
    __tablename__ = "suppression_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    metric_pattern = Column(String(255), nullable=False)  # regex pattern
    suppression_window_start = Column(DateTime, nullable=True)
    suppression_window_end = Column(DateTime, nullable=True)
    is_maintenance_window = Column(Boolean, default=False)
    conditions = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
