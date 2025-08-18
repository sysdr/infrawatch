from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime, timedelta, timezone

Base = declarative_base()

class MetricType:
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SET = "set"

class RetentionTier:
    REALTIME = "realtime"
    RECENT = "recent" 
    DAILY = "daily"
    HISTORICAL = "historical"
    ARCHIVE = "archive"

class MetricsRaw(Base):
    __tablename__ = 'metrics_raw'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, nullable=False, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False, default=MetricType.GAUGE)
    value = Column(Float, nullable=False)
    tags = Column(Text, nullable=True, default='{}')  # JSON as text for SQLite compatibility
    labels = Column(Text, nullable=True, default='{}')  # JSON as text for SQLite compatibility
    retention_tier = Column(String(50), nullable=False, default=RetentionTier.RECENT)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_timestamp_metric', 'timestamp', 'metric_name'),
        Index('idx_metric_type_tags', 'metric_type', 'tags'),
        Index('idx_retention_expires', 'retention_tier', 'expires_at'),
        Index('idx_timestamp_desc', 'timestamp'),
    )

class MetricCategories(Base):
    __tablename__ = 'metric_categories'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    metric_type = Column(String(50), nullable=False)
    default_retention_days = Column(Integer, default=30)
    aggregation_intervals = Column(Text, default='["1m", "5m", "1h", "1d"]')  # JSON as text
    tags_whitelist = Column(Text, default='[]')  # JSON as text
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RetentionPolicies(Base):
    __tablename__ = 'retention_policies'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_name = Column(String(100), unique=True, nullable=False)
    metric_pattern = Column(String(255), nullable=False)  # regex pattern
    retention_days = Column(Integer, nullable=False)
    aggregation_strategy = Column(String(50), default='avg')
    priority = Column(Integer, default=100)  # lower = higher priority
    conditions = Column(Text, default='{}')  # JSON as text
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MetricAggregations(Base):
    __tablename__ = 'metric_aggregations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(255), nullable=False)
    interval = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d
    timestamp = Column(DateTime, nullable=False)
    avg_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    sum_value = Column(Float)
    count_value = Column(Integer)
    p95_value = Column(Float)
    p99_value = Column(Float)
    tags = Column(Text, default='{}')  # JSON as text
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_metric_interval_timestamp', 'metric_name', 'interval', 'timestamp'),
        Index('idx_aggregation_timestamp_desc', 'timestamp'),
    )

class MetricIndexes(Base):
    __tablename__ = 'metric_indexes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(255), unique=True, nullable=False)
    metric_type = Column(String(50), nullable=False)
    category = Column(String(100))
    tags = Column(Text, default='{}')  # JSON as text
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    data_points_count = Column(Integer, default=0)
    avg_frequency = Column(Float, default=0.0)  # points per minute
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_metric_search', 'metric_name', 'category', 'is_active'),
    )
