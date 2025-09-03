from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class MetricEntry(Base):
    __tablename__ = "metric_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), index=True)
    tags = Column(String(1000))  # JSON string for tags
    source = Column(String(100), index=True)
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_name_timestamp', 'name', 'timestamp'),
        Index('idx_source_timestamp', 'source', 'timestamp'),
    )

class MetricSummary(Base):
    __tablename__ = "metric_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    min_value = Column(Float)
    max_value = Column(Float)
    avg_value = Column(Float)
    count = Column(Integer)
    window_start = Column(DateTime, index=True)
    window_end = Column(DateTime, index=True)
    
    __table_args__ = (
        Index('idx_name_window', 'name', 'window_start', 'window_end'),
    )
