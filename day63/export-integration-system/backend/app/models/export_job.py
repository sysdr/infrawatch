from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExportFormat(str, enum.Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    export_type = Column(String, nullable=False)
    format = Column(SQLEnum(ExportFormat), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    filters = Column(JSON, default={})
    row_count = Column(Integer, default=0)
    file_path = Column(String)
    file_size = Column(Integer, default=0)
    checksum = Column(String)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
