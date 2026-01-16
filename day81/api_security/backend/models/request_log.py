from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_id = Column(String(64), index=True, nullable=False)
    
    # Request details
    method = Column(String(10), nullable=False)
    path = Column(String(512), nullable=False)
    source_ip = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(512))
    
    # Security validation
    signature_valid = Column(Boolean, default=False)
    ip_whitelisted = Column(Boolean, default=False)
    rate_limited = Column(Boolean, default=False)
    
    # Response
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    
    # Additional metadata
    headers = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
