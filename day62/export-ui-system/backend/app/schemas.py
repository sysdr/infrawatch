from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ExportConfig(BaseModel):
    data_source: str
    start_date: str
    end_date: str
    format_type: str = Field(..., pattern="^(CSV|JSON|EXCEL|PDF)$")
    filters: Optional[Dict[str, Any]] = {}
    fields: Optional[List[str]] = []
    options: Optional[Dict[str, Any]] = {}

class ExportRequest(BaseModel):
    user_id: str
    config: ExportConfig

class ExportResponse(BaseModel):
    job_id: str
    status: str
    message: str

class ExportStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    format_type: str
    file_size: Optional[int]
    row_count: Optional[int]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    download_url: Optional[str]
    error_message: Optional[str]

class ScheduleRequest(BaseModel):
    user_id: str
    name: str
    cron_expression: str
    timezone: str = "UTC"
    export_config: ExportConfig

class ScheduleResponse(BaseModel):
    schedule_id: str
    name: str
    cron_expression: str
    next_run_time: datetime
    message: str
