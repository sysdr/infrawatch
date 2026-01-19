from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, index=True, nullable=False)
    action_type = Column(String(100), index=True, nullable=False)
    actor = Column(String(100), index=True, nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(200), nullable=True)
    action_result = Column(String(20), nullable=False)
    ip_address = Column(String(50), nullable=False)
    user_agent = Column(Text, nullable=True)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    audit_metadata = Column("audit_metadata", JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
