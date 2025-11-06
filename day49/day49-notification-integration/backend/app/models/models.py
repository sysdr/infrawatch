from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base

class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    NOTIFIED = "NOTIFIED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"

class NotificationChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    SLACK = "SLACK"

class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True)
    alert_type = Column(String)
    severity = Column(SQLEnum(AlertSeverity))
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.NEW)
    message = Column(Text)
    alert_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    escalation_level = Column(Integer, default=0)
    
    notifications = relationship("Notification", back_populates="alert")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    email = Column(String)
    phone = Column(String, nullable=True)
    slack_id = Column(String, nullable=True)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    user_id = Column(String, index=True)
    channel = Column(SQLEnum(NotificationChannel))
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    idempotency_key = Column(String, unique=True, index=True)
    message = Column(Text)
    notification_metadata = Column(JSON, default={})
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    alert = relationship("Alert", back_populates="notifications")

class EscalationPolicy(Base):
    __tablename__ = "escalation_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True)
    severity = Column(SQLEnum(AlertSeverity))
    policy_config = Column(JSON)  # [{level: 0, users: [...], timeout_minutes: 5}, ...]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
