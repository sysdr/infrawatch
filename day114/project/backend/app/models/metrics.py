from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class WebVitalMetric(Base):
    __tablename__ = "web_vital_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(20), nullable=False, index=True)      # LCP, CLS, FID, TTFB, INP
    value = Column(Float, nullable=False)
    rating = Column(String(10))                                        # good, needs-improvement, poor
    route = Column(String(255), default="/")
    session_id = Column(String(64), index=True)
    user_agent = Column(Text)
    connection_type = Column(String(20))
    prefetch_used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)

class BundleMetric(Base):
    __tablename__ = "bundle_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_name = Column(String(255), nullable=False)
    chunk_size_bytes = Column(Integer)
    load_time_ms = Column(Float)
    cached = Column(Boolean, default=False)
    route = Column(String(255))
    session_id = Column(String(64))
    created_at = Column(DateTime, server_default=func.now(), index=True)

class ServiceWorkerEvent(Base):
    __tablename__ = "service_worker_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50))     # install, activate, fetch, cache_hit, cache_miss
    cache_strategy = Column(String(50)) # cache-first, network-first, stale-while-revalidate
    url = Column(Text)
    served_from_cache = Column(Boolean, default=False)
    session_id = Column(String(64))
    created_at = Column(DateTime, server_default=func.now(), index=True)
