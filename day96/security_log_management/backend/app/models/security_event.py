from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Index
from app.utils.database import Base
from datetime import datetime
import hashlib
import json

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    user_id = Column(String(100), index=True)
    username = Column(String(255))
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    resource = Column(String(500))
    action = Column(String(100))
    result = Column(String(20))  # success, failure, blocked
    details = Column(JSON)
    anomaly_score = Column(Float, default=0.0)
    threat_indicators = Column(JSON)
    previous_hash = Column(String(64))
    event_hash = Column(String(64), unique=True, index=True)
    correlation_id = Column(String(100), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_severity_timestamp', 'severity', 'timestamp'),
        Index('idx_type_timestamp', 'event_type', 'timestamp'),
    )
    
    def calculate_hash(self):
        """Calculate cryptographic hash for audit trail integrity"""
        data = f"{self.event_type}{self.user_id}{self.timestamp}{self.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "severity": self.severity,
            "user_id": self.user_id,
            "username": self.username,
            "ip_address": self.ip_address,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "details": self.details,
            "anomaly_score": self.anomaly_score,
            "threat_indicators": self.threat_indicators,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
