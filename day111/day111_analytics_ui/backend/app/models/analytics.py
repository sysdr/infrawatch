from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), default="")
    tags = Column(JSONB, default=dict)
    recorded_at = Column(DateTime(timezone=True), default=utcnow, index=True)

class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    artifact_path = Column(String(255), nullable=False)
    metrics = Column(JSONB, default=dict)
    features = Column(JSONB, default=list)
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime(timezone=True), default=utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    config = Column(JSONB, nullable=False)
    schedule_cron = Column(String(100), nullable=True)
    output_format = Column(String(20), default="pdf")
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    last_run_at = Column(DateTime(timezone=True), nullable=True)

class AnalyticsConfig(Base):
    __tablename__ = "analytics_configs"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSONB, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
