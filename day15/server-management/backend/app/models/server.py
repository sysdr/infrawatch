from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import uuid

# Association table for server tags
server_tags = Table('server_tags',
    Base.metadata,
    Column('server_id', UUID(as_uuid=True), ForeignKey('servers.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Server(Base):
    __tablename__ = "servers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)  # Support IPv6
    port = Column(Integer, default=22)
    
    # Server specifications
    cpu_cores = Column(Integer)
    memory_gb = Column(Integer)
    storage_gb = Column(Integer)
    os_type = Column(String(50))
    os_version = Column(String(100))
    
    # Status and health
    status = Column(String(50), default="provisioning")  # provisioning, active, draining, terminated
    health_status = Column(String(50), default="unknown")  # healthy, degraded, failed, unknown
    last_heartbeat = Column(DateTime(timezone=True))
    
    # Categorization
    environment = Column(String(50))  # dev, staging, prod
    region = Column(String(50))
    availability_zone = Column(String(50))
    server_type = Column(String(50))  # web, database, cache, worker
    
    # Metadata and configuration
    server_metadata = Column(JSONB)
    configuration = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))
    
    # Relationships
    tags = relationship("Tag", secondary=server_tags, back_populates="servers")
    health_checks = relationship("HealthCheck", back_populates="server")
    dependencies = relationship("ServerDependency", foreign_keys="ServerDependency.server_id", back_populates="server")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))  # environment, service, version, custom
    color = Column(String(7), default="#3B82F6")  # Hex color
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    servers = relationship("Server", secondary=server_tags, back_populates="tags")

class HealthCheck(Base):
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    
    # Health metrics
    cpu_usage = Column(Integer)  # Percentage
    memory_usage = Column(Integer)  # Percentage  
    disk_usage = Column(Integer)  # Percentage
    network_latency = Column(Integer)  # Milliseconds
    
    # Application health
    service_status = Column(JSONB)  # Per-service health status
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    # Check metadata
    check_type = Column(String(50), default="automated")  # automated, manual
    status = Column(String(50))  # healthy, warning, critical
    message = Column(Text)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    server = relationship("Server", back_populates="health_checks")

class ServerDependency(Base):
    __tablename__ = "server_dependencies"
    
    id = Column(Integer, primary_key=True)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    depends_on_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    
    dependency_type = Column(String(50))  # network, service, data, deployment
    description = Column(Text)
    is_critical = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    server = relationship("Server", foreign_keys=[server_id])
    depends_on = relationship("Server", foreign_keys=[depends_on_id])
