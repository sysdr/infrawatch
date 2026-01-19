from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False)
    event_type = Column(String(100), index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)
    source = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=True)
    user_id = Column(String(100), index=True, nullable=True)
    ip_address = Column(String(50), index=True, nullable=False)
    user_agent = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    event_metadata = Column("event_metadata", JSON, nullable=True)
    threat_score = Column(Integer, default=0)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
