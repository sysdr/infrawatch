from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from ..database import Base

class MetricSample(Base):
    __tablename__ = "metric_samples"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    request_rate = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    latency_p99 = Column(Float, nullable=False)
    disk_io = Column(Float, nullable=False)
    network_in = Column(Float, nullable=False)
    network_out = Column(Float, nullable=False)

class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    anomaly_score = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, default=False)
    affected_metrics = Column(JSON)
    severity = Column(String(20), default="low")
    description = Column(Text)

class ModelMetadata(Base):
    __tablename__ = "model_metadata"
    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(50), nullable=False)
    trained_at = Column(DateTime, default=func.now())
    training_samples = Column(Integer)
    hyperparameters = Column(JSON)
    metrics = Column(JSON)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class ForecastResult(Base):
    __tablename__ = "forecast_results"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    metric_name = Column(String(50))
    forecast_data = Column(JSON)
    lower_bound = Column(JSON)
    upper_bound = Column(JSON)
    horizon_hours = Column(Integer, default=24)
    rmse = Column(Float)

class PatternCluster(Base):
    __tablename__ = "pattern_clusters"
    id = Column(Integer, primary_key=True, index=True)
    analyzed_at = Column(DateTime, default=func.now())
    cluster_id = Column(Integer)
    cluster_label = Column(String(50))
    centroid = Column(JSON)
    sample_count = Column(Integer)
    silhouette_score = Column(Float)
