from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from app.utils.database import Base
from datetime import datetime

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default="open", index=True)
    incident_type = Column(String(50), index=True)
    affected_users = Column(JSON)
    affected_resources = Column(JSON)
    detection_method = Column(String(100))
    confidence_score = Column(Integer)
    auto_response_taken = Column(Boolean, default=False)
    response_actions = Column(JSON)
    assigned_to = Column(String(255))
    related_events = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "incident_type": self.incident_type,
            "affected_users": self.affected_users,
            "affected_resources": self.affected_resources,
            "detection_method": self.detection_method,
            "confidence_score": self.confidence_score,
            "auto_response_taken": self.auto_response_taken,
            "response_actions": self.response_actions,
            "assigned_to": self.assigned_to,
            "related_events": self.related_events,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes
        }
