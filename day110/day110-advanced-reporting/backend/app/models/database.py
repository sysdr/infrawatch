from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

DATABASE_URL = "sqlite:///./reporting.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ReportState(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    GENERATING = "GENERATING"
    FORMATTING = "FORMATTING"
    DISTRIBUTING = "DISTRIBUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ReportTemplate(Base):
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    version = Column(Integer, default=1)
    query_config = Column(JSON)  # Metrics, filters, aggregations
    layout_config = Column(JSON)  # Sections, visualizations
    parent_template_id = Column(Integer, nullable=True)  # For inheritance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ReportDefinition(Base):
    __tablename__ = "report_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    template_id = Column(Integer)
    parameters = Column(JSON)  # Runtime parameters
    output_formats = Column(JSON)  # ["pdf", "excel", "csv", "json"]
    state = Column(SQLEnum(ReportState), default=ReportState.DRAFT)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportSchedule(Base):
    __tablename__ = "report_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, index=True)
    cron_expression = Column(String)  # "0 9 * * MON" = 9 AM every Monday
    timezone = Column(String, default="UTC")
    is_active = Column(Boolean, default=True)
    next_run = Column(DateTime)
    last_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DistributionList(Base):
    __tablename__ = "distribution_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    recipients = Column(JSON)  # [{"type": "email", "address": "user@example.com"}]
    channels = Column(JSON)  # ["email", "webhook", "s3"]
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportExecution(Base):
    __tablename__ = "report_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, index=True)
    state = Column(SQLEnum(ReportState))
    output_paths = Column(JSON)  # {"pdf": "path/to/file.pdf", "excel": "..."}
    execution_time_ms = Column(Integer)
    error_message = Column(Text, nullable=True)
    distributed_to = Column(JSON)  # Delivery confirmations
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
