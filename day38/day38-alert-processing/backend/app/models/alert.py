from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum as SQLEnum, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import uuid

Base = declarative_base()

class AlertState(Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"

class AlertSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    metric_name = Column(String(100), nullable=False)
    service_name = Column(String(100), nullable=False)
    current_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    
    # State management
    state = Column(SQLEnum(AlertState), default=AlertState.NEW)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.MEDIUM)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Ownership
    acknowledged_by = Column(String(100))
    resolved_by = Column(String(100))
    
    # Metadata
    auto_resolved = Column(Boolean, default=False)
    occurrence_count = Column(Integer, default=1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "metric_name": self.metric_name,
            "service_name": self.service_name,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "state": self.state.value,
            "severity": self.severity.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_by": self.resolved_by,
            "auto_resolved": self.auto_resolved,
            "occurrence_count": self.occurrence_count
        }
    
    def get_duration(self) -> Optional[int]:
        """Get alert duration in seconds"""
        if self.resolved_at and self.created_at:
            return int((self.resolved_at - self.created_at).total_seconds())
        elif self.created_at:
            return int((datetime.utcnow() - self.created_at).total_seconds())
        return None
    
    def get_severity_color(self) -> str:
        """Get color code for severity"""
        colors = {
            AlertSeverity.LOW: "#2ECC71",
            AlertSeverity.MEDIUM: "#F39C12", 
            AlertSeverity.HIGH: "#E67E22",
            AlertSeverity.CRITICAL: "#E74C3C"
        }
        return colors.get(self.severity, "#95A5A6")
