from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_type = Column(String, nullable=False, index=True)
    cloud_provider = Column(String, nullable=False, index=True)
    region = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="unknown", index=True)
    tags = Column(JSON, default=dict)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_synced = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('ix_resources_type_provider', 'resource_type', 'cloud_provider'),
    )

class ResourceDependency(Base):
    __tablename__ = "resource_dependencies"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(String, ForeignKey('resources.id', ondelete='CASCADE'), index=True)
    target_id = Column(String, ForeignKey('resources.id', ondelete='CASCADE'), index=True)
    dependency_type = Column(String, default="network")
    strength = Column(Float, default=1.0)
    created_at = Column(DateTime, server_default=func.now())

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(String, ForeignKey('resources.id', ondelete='CASCADE'), index=True)
    timestamp = Column(DateTime, index=True, server_default=func.now())
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    network_in = Column(Float, default=0.0)
    network_out = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    
    __table_args__ = (
        Index('ix_metrics_resource_time', 'resource_id', 'timestamp'),
    )

class Cost(Base):
    __tablename__ = "costs"
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(String, ForeignKey('resources.id', ondelete='CASCADE'), index=True)
    date = Column(DateTime, index=True)
    amount = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    service_type = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('ix_costs_resource_date', 'resource_id', 'date'),
    )
