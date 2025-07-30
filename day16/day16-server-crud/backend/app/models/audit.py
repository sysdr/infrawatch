from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String, index=True)
    resource_id = Column(String, index=True)
    action = Column(String, index=True)
    user_id = Column(String, index=True)
    tenant_id = Column(String, index=True)
    changes = Column(JSON)
    audit_metadata = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String)
    user_agent = Column(Text)
