from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Server(Base):
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    hostname = Column(String, unique=True, index=True, nullable=False)
    ip_address = Column(String, index=True, nullable=False)
    status = Column(String, default="active", index=True)
    server_type = Column(String, index=True)
    environment = Column(String, index=True)
    region = Column(String, index=True)
    specs = Column(JSON)
    server_metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])
    tenant_id = Column(String, index=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Soft delete flag
    is_deleted = Column(Boolean, default=False)
    
    # Version control for optimistic locking
    version = Column(Integer, default=1)
