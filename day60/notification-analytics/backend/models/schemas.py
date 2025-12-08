from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class MetricData(Base):
    __tablename__ = "metric_data"
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True, nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    tags = Column(JSON, default={})
    __table_args__ = (Index('idx_metric_timestamp', 'metric_name', 'timestamp'),)

class StatisticalBaseline(Base):
    __tablename__ = "statistical_baselines"
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True, nullable=False)
    window_size = Column(Integer, nullable=False)
    mean = Column(Float, nullable=False)
    median = Column(Float, nullable=False)
    std_dev = Column(Float, nullable=False)
    p95 = Column(Float, nullable=False)
    p99 = Column(Float, nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    sample_count = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True, nullable=False)
    anomaly_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    value = Column(Float, nullable=False)
    expected_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    is_resolved = Column(Boolean, default=False)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True, nullable=False)
    prediction_timestamp = Column(DateTime, nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Initialize database
def init_db():
    db_url = os.getenv("DATABASE_URL", "sqlite:///./analytics.db")
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine), engine
