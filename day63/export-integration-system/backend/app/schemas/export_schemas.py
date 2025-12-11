from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExportJobCreate(BaseModel):
    export_type: str
    format: ExportFormat
    filters: Optional[Dict[str, Any]] = {}
    compress: bool = False

class ExportJobResponse(BaseModel):
    id: str
    user_id: str
    export_type: str
    format: str
    status: str
    row_count: int
    file_size: int
    file_path: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ExportScheduleCreate(BaseModel):
    name: str
    export_type: str
    format: ExportFormat
    filters: Optional[Dict[str, Any]] = {}
    schedule_expression: str
    timezone: str = "UTC"
    email_recipients: List[EmailStr] = []

class ExportScheduleResponse(BaseModel):
    id: str
    user_id: str
    name: str
    export_type: str
    format: str
    schedule_expression: str
    enabled: bool
    next_run_at: Optional[datetime]
    run_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
