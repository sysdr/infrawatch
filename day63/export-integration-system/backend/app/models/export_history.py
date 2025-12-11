from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ExportHistory(Base):
    __tablename__ = "export_history"
    
    id = Column(String, primary_key=True)
    schedule_id = Column(String)
    job_id = Column(String, nullable=False)
    success = Column(Boolean, default=False)
    execution_time_seconds = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
