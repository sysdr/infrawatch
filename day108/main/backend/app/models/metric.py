from sqlalchemy import Column, String, JSON, DateTime, Float, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class MetricDefinition(Base):
    __tablename__ = "metric_definitions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    formula = Column(Text, nullable=False)
    variables = Column(JSON, nullable=False)  # List of required variables
    category = Column(String(100), index=True)
    unit = Column(String(50))
    aggregation_type = Column(String(50))  # sum, avg, max, min, count
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    validation_rules = Column(JSON)  # Min, max, data type constraints

class MetricCalculation(Base):
    __tablename__ = "metric_calculations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_id = Column(String(36), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    input_values = Column(JSON, nullable=False)
    calculated_value = Column(Float)
    execution_time_ms = Column(Float)
    status = Column(String(50))  # success, failed, timeout
    error_message = Column(Text)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_id = Column(String(36), nullable=False, index=True)
    avg_execution_time = Column(Float)
    max_execution_time = Column(Float)
    min_execution_time = Column(Float)
    total_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
