from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id          = Column(Integer, primary_key=True, index=True)
    event_type  = Column(String(64), index=True)
    user_id     = Column(String(64), nullable=True)
    session_id  = Column(String(64), nullable=True)
    page        = Column(String(256), nullable=True)
    duration_ms = Column(Float, nullable=True)
    revenue     = Column(Float, nullable=True, default=0.0)
    properties  = Column(JSON, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class HourlyMetric(Base):
    __tablename__ = "hourly_metrics"
    id            = Column(Integer, primary_key=True, index=True)
    hour_bucket   = Column(DateTime(timezone=True), index=True)
    page_views    = Column(Integer, default=0)
    sessions      = Column(Integer, default=0)
    revenue       = Column(Float, default=0.0)
    response_time = Column(Float, default=0.0)
    error_rate    = Column(Float, default=0.0)

class MLModel(Base):
    __tablename__ = "ml_models"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(128))
    model_type  = Column(String(64))
    metrics     = Column(JSON, nullable=True)
    is_active   = Column(Boolean, default=False)
    model_path  = Column(String(512), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    id              = Column(Integer, primary_key=True, index=True)
    model_id        = Column(Integer, nullable=True)
    target_hour     = Column(DateTime(timezone=True), index=True)
    predicted_value = Column(Float)
    actual_value    = Column(Float, nullable=True)
    is_anomaly      = Column(Boolean, default=False)
    anomaly_score   = Column(Float, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
