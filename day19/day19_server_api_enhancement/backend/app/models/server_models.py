from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

# Association table for server-group many-to-many relationship
server_group_association = Table(
    'server_groups',
    Base.metadata,
    Column('server_id', Integer, ForeignKey('servers.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class Server(Base):
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    hostname = Column(String, unique=True, index=True)
    ip_address = Column(String, index=True)
    status = Column(String, default="unknown")
    region = Column(String, index=True)
    instance_type = Column(String)
    cpu_cores = Column(Integer)
    memory_gb = Column(Integer)
    storage_gb = Column(Integer)
    os_type = Column(String)
    tags = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    groups = relationship("Group", secondary=server_group_association, back_populates="servers")

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    color = Column(String, default="#3B82F6")
    created_at = Column(DateTime, default=datetime.utcnow)
    parent_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    
    # Relationships
    servers = relationship("Server", secondary=server_group_association, back_populates="groups")
    children = relationship("Group", backref="parent", remote_side=[id])

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    config = Column(JSON)
    version = Column(String, default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BulkTask(Base):
    __tablename__ = "bulk_tasks"
    
    id = Column(String, primary_key=True, index=True)
    action = Column(String, nullable=False)
    server_ids = Column(JSON)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    total = Column(Integer)
    result = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
