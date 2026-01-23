from sqlalchemy import Column, String, Integer, DateTime, JSON, Index, Text
from sqlalchemy.sql import func
from app.utils.database import Base

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True)
    resource_type = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False, index=True)
    region = Column(String, index=True)
    resource_metadata = Column("metadata", JSON)  # Column name in DB is 'metadata', but attribute is 'resource_metadata'
    config_hash = Column(String, index=True)
    state = Column(String, default="DISCOVERED", index=True)
    discovered_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_type_provider', 'resource_type', 'provider'),
    )

class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String, nullable=False, index=True)
    target_id = Column(String, nullable=False, index=True)
    relationship_type = Column(String, nullable=False)
    relationship_metadata = Column("metadata", JSON)  # Column name in DB is 'metadata', but attribute is 'relationship_metadata'
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_source_target', 'source_id', 'target_id'),
    )

class Change(Base):
    __tablename__ = "changes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String, nullable=False, index=True)
    change_type = Column(String, nullable=False)  # CREATED, MODIFIED, DELETED
    old_hash = Column(String)
    new_hash = Column(String)
    diff = Column(JSON)
    detected_at = Column(DateTime, server_default=func.now(), index=True)
