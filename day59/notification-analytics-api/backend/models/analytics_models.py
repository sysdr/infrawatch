from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Float, Index, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class NotificationEvent(Base):
    """Raw notification events table"""
    __tablename__ = 'notification_events'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, index=True)
    channel = Column(String(20), nullable=False, index=True)
    template_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    processing_time_ms = Column(Integer)
    event_metadata = Column('metadata', JSONB)
    
    __table_args__ = (
        Index('idx_events_time_channel', 'created_at', 'channel'),
        Index('idx_events_time_status', 'created_at', 'status'),
    )

class NotificationMetricHourly(Base):
    """Pre-aggregated hourly metrics"""
    __tablename__ = 'notification_metrics_hourly'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    time_bucket = Column(DateTime, nullable=False, index=True)
    channel = Column(String(20), nullable=False, index=True)
    template_id = Column(Integer, index=True)
    status = Column(String(20), nullable=False, index=True)
    event_count = Column(BigInteger, default=0)
    avg_processing_time = Column(Float)
    
    __table_args__ = (
        Index('idx_metrics_time_channel_status', 'time_bucket', 'channel', 'status'),
    )

class NotificationMetricDaily(Base):
    """Pre-aggregated daily metrics"""
    __tablename__ = 'notification_metrics_daily'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    channel = Column(String(20), nullable=False, index=True)
    template_id = Column(Integer, index=True)
    status = Column(String(20), nullable=False, index=True)
    event_count = Column(BigInteger, default=0)
    avg_processing_time = Column(Float)
    
    __table_args__ = (
        Index('idx_daily_metrics_date_channel', 'date', 'channel'),
    )

class CustomMetric(Base):
    """User-defined custom metrics"""
    __tablename__ = 'custom_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    formula = Column(String(500), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
