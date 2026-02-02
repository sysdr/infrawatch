from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./loganalysis.db")

_connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LogPattern(Base):
    __tablename__ = "log_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_signature = Column(String(500), unique=True, index=True)
    pattern_template = Column(Text)
    category = Column(String(100))
    severity = Column(String(50))
    frequency_count = Column(Integer, default=0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_critical = Column(Boolean, default=False)
    extra_data = Column(JSON)  # JSON metadata (avoids SQLAlchemy reserved 'metadata')

class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_name = Column(String(200))
    metric_value = Column(Float)
    baseline_mean = Column(Float)
    baseline_stddev = Column(Float)
    z_score = Column(Float)
    anomaly_type = Column(String(100))  # spike, drop, trend_change
    severity = Column(String(50))
    source = Column(String(200))
    extra_data = Column(JSON)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

class TrendData(Base):
    __tablename__ = "trend_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_name = Column(String(200), index=True)
    time_window = Column(String(50))  # 5min, 1hour, 1day
    value = Column(Float)
    moving_average = Column(Float)
    trend_direction = Column(String(50))  # up, down, stable
    extra_data = Column(JSON)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    alert_type = Column(String(100))  # pattern, anomaly, trend
    severity = Column(String(50))  # critical, high, medium, low
    title = Column(String(500))
    description = Column(Text)
    source = Column(String(200))
    related_entity_id = Column(Integer)
    related_entity_type = Column(String(100))
    status = Column(String(50), default="active")  # active, acknowledged, resolved
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
