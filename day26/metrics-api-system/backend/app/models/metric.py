from sqlalchemy import Column, Integer, String, DateTime, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True)
    tags = Column(String, nullable=True)  # JSON string
    source = Column(String, nullable=True)
    
    # Composite index for efficient time-series queries
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'name', 'timestamp'),
        Index('idx_metrics_timestamp', 'timestamp'),
    )

class AggregatedMetric(Base):
    __tablename__ = "aggregated_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False, index=True)
    interval_start = Column(DateTime(timezone=True), nullable=False)
    interval_end = Column(DateTime(timezone=True), nullable=False)
    interval_duration = Column(String, nullable=False)  # '5m', '1h', '1d'
    aggregation_type = Column(String, nullable=False)  # 'avg', 'sum', 'count', 'p95'
    value = Column(Float, nullable=False)
    sample_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    __table_args__ = (
        Index('idx_agg_metrics_query', 'metric_name', 'interval_start', 'interval_end', 'aggregation_type'),
    )
