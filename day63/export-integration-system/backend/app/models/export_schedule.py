from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ExportSchedule(Base):
    __tablename__ = "export_schedules"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    export_type = Column(String, nullable=False)
    format = Column(String, nullable=False)
    filters = Column(JSON, default={})
    schedule_expression = Column(String, nullable=False)  # Cron expression
    timezone = Column(String, default="UTC")
    email_recipients = Column(JSON, default=[])
    enabled = Column(Boolean, default=True)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    run_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
