from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True)
    status = Column(String(50), default="QUEUED")  # QUEUED, PROCESSING, COMPLETED, FAILED, CANCELLED
    format_type = Column(String(20))  # CSV, JSON, EXCEL, PDF
    config = Column(JSON)
    file_path = Column(String(500))
    file_size = Column(Integer)
    row_count = Column(Integer)
    progress = Column(Float, default=0.0)
    error_message = Column(Text)
    download_url = Column(String(1000))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

class ScheduledExport(Base):
    __tablename__ = "scheduled_exports"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True)
    name = Column(String(200))
    cron_expression = Column(String(100))
    timezone = Column(String(50))
    export_config = Column(JSON)
    enabled = Column(Boolean, default=True)
    next_run_time = Column(DateTime)
    last_run_time = Column(DateTime)
    run_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
