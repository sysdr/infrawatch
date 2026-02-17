from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Prefer PostgreSQL if DATABASE_URL is set; otherwise use SQLite (no extra setup)
_default_pg = "postgresql://postgres:postgres@localhost:5432/correlation_db"
_raw_url = os.getenv("DATABASE_URL", "").strip() or _default_pg

if _raw_url.startswith("sqlite"):
    _engine_kw = {"connect_args": {"check_same_thread": False}}
else:
    _engine_kw = {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20}

# If default was postgres, try SQLite fallback when postgres is unreachable
if _raw_url == _default_pg:
    try:
        _test = create_engine(_raw_url, pool_pre_ping=True)
        with _test.connect() as c:
            c.execute(text("SELECT 1"))
        DATABASE_URL = _raw_url
        engine = create_engine(DATABASE_URL, **_engine_kw)
    except Exception:
        _sqlite_path = os.path.join(os.path.dirname(__file__), "..", "correlation.db")
        DATABASE_URL = f"sqlite:///{os.path.abspath(_sqlite_path)}"
        engine = create_engine(DATABASE_URL, **_engine_kw)
else:
    DATABASE_URL = _raw_url
    engine = create_engine(DATABASE_URL, **_engine_kw)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    service = Column(String, index=True)
    metric_type = Column(String)
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class MetricData(Base):
    __tablename__ = "metric_data"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, index=True)
    timestamp = Column(DateTime, index=True)
    value = Column(Float)
    

class Correlation(Base):
    __tablename__ = "correlations"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_a_id = Column(Integer, index=True)
    metric_b_id = Column(Integer, index=True)
    coefficient = Column(Float)
    correlation_type = Column(String)  # pearson, spearman
    p_value = Column(Float)
    state = Column(String, default="candidate")  # candidate, validating, active, decaying, expired
    lag_seconds = Column(Integer, default=0)
    window_size = Column(Integer)
    detected_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_metadata = Column(JSON)


class CausalRelation(Base):
    __tablename__ = "causal_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    cause_metric_id = Column(Integer, index=True)
    effect_metric_id = Column(Integer, index=True)
    granger_score = Column(Float)
    confidence = Column(Float)
    lag_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class ImpactAssessment(Base):
    __tablename__ = "impact_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    root_metric_id = Column(Integer, index=True)
    affected_metrics = Column(JSON)  # list of {metric_id, probability, severity}
    impact_radius = Column(Integer)
    total_services_affected = Column(Integer)
    assessment_time = Column(DateTime, default=datetime.utcnow)
    


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        raise  # let main.py handle and log


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
