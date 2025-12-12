from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text)
    layout = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    template_id = Column(String, ForeignKey("templates.id"), nullable=True)
    
    widgets = relationship("Widget", back_populates="dashboard", cascade="all, delete-orphan")

class Widget(Base):
    __tablename__ = "widgets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    dashboard_id = Column(String, ForeignKey("dashboards.id"), nullable=False)
    widget_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    config = Column(JSON, default=dict)
    position = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dashboard = relationship("Dashboard", back_populates="widgets")

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text)
    layout = Column(JSON, default=list)
    widget_configs = Column(JSON, default=list)
    is_public = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
