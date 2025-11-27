from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON
from sqlalchemy.sql import func
from app.models.database import Base
import enum

class ExportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class ExportFormat(str, enum.Enum):
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True)
    export_format = Column(Enum(ExportFormat), nullable=False)
    status = Column(Enum(ExportStatus), default=ExportStatus.PENDING, index=True)
    filters = Column(JSON)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    file_path = Column(String(500))
    file_size = Column(Integer)
    download_url = Column(String(500))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
