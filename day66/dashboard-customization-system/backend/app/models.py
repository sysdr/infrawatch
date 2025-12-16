from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    config = Column(JSONB, nullable=False)
    theme = Column(String(50), default='light')
    is_template = Column(Boolean, default=False, index=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_dashboard_config', config, postgresql_using='gin'),
    )

class DashboardVersion(Base):
    __tablename__ = "dashboard_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey('dashboards.id', ondelete='CASCADE'), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    config = Column(JSONB, nullable=False)
    theme = Column(String(50))
    changed_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DashboardShare(Base):
    __tablename__ = "dashboard_shares"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey('dashboards.id', ondelete='CASCADE'), nullable=False, index=True)
    share_token = Column(String(255), unique=True, nullable=False, index=True)
    permission = Column(String(20), default='view')  # view, edit, admin
    expires_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    theme_preference = Column(String(50), default='light')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
