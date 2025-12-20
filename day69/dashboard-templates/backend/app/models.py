from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), default="viewer")  # admin, editor, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    templates = relationship("Template", back_populates="author")
    dashboards = relationship("Dashboard", back_populates="owner")

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    version = Column(String(20), nullable=False)  # semantic versioning
    config = Column(JSON, nullable=False)  # dashboard configuration
    parent_version_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visibility = Column(String(20), default="private")  # private, team, public
    role_access = Column(JSON, default=list)  # list of roles that can access
    category = Column(String(100), index=True)
    tags = Column(JSON, default=list)
    status = Column(String(20), default="draft")  # draft, published, deprecated, archived, deleted
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    preview_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    author = relationship("User", back_populates="templates")
    parent_version = relationship("Template", remote_side=[id], foreign_keys=[parent_version_id])
    variables = relationship("TemplateVariable", back_populates="template")
    
    __table_args__ = (
        Index('idx_template_search', 'name', 'category', 'status'),
        Index('idx_template_author', 'author_id', 'status'),
    )

class TemplateVariable(Base):
    __tablename__ = "template_variables"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    variable_type = Column(String(50), default="string")  # string, number, boolean, select
    default_value = Column(String(255))
    options = Column(JSON, default=list)  # for select type
    required = Column(Boolean, default=True)
    
    template = relationship("Template", back_populates="variables")

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    config = Column(JSON, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    template_version = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="dashboards")
    template = relationship("Template")

class TemplateRating(Base):
    __tablename__ = "template_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    review = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_unique_rating', 'template_id', 'user_id', unique=True),
    )
