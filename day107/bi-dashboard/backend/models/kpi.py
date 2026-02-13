from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class KPIMetric(Base):
    __tablename__ = "kpi_metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, index=True)
    unit = Column(String)
    calculation_method = Column(String)
    target_value = Column(Float)
    critical_threshold = Column(Float)
    warning_threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    values = relationship("KPIValue", back_populates="metric", cascade="all, delete-orphan")

class KPIValue(Base):
    __tablename__ = "kpi_values"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("kpi_metrics.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    value = Column(Float, nullable=False)
    dimensions = Column(JSON)
    extra_metadata = Column(JSON)  # DB column: extra_metadata (avoid shadowing Base.metadata)

    metric = relationship("KPIMetric", back_populates="values")

    __table_args__ = (
        Index('idx_metric_timestamp', 'metric_id', 'timestamp'),
        Index('idx_timestamp_metric', 'timestamp', 'metric_id'),
    )

class TrendAnalysis(Base):
    __tablename__ = "trend_analyses"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("kpi_metrics.id"), nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow, index=True)
    trend_direction = Column(String)
    trend_strength = Column(Float)
    moving_average_7d = Column(Float)
    moving_average_30d = Column(Float)
    standard_deviation = Column(Float)
    z_score = Column(Float)
    is_anomaly = Column(Integer, default=0)
    confidence_level = Column(Float)
    analysis_metadata = Column(JSON)

    metric = relationship("KPIMetric")

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("kpi_metrics.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False, index=True)
    predicted_value = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    model_type = Column(String)
    model_parameters = Column(JSON)
    accuracy_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    metric = relationship("KPIMetric")

    __table_args__ = (
        Index('idx_forecast_metric_date', 'metric_id', 'forecast_date'),
    )

class ExecutiveReport(Base):
    __tablename__ = "executive_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    file_path = Column(String)
    summary = Column(JSON)
    key_insights = Column(JSON)
    status = Column(String, default="completed")
