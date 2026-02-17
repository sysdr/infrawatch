from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class OutputFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

class ReportState(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    GENERATING = "GENERATING"
    FORMATTING = "FORMATTING"
    DISTRIBUTING = "DISTRIBUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    query_config: Dict[str, Any]
    layout_config: Dict[str, Any]
    parent_template_id: Optional[int] = None

class TemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    version: int
    query_config: Dict[str, Any]
    layout_config: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportCreate(BaseModel):
    name: str
    template_id: int
    parameters: Dict[str, Any] = {}
    output_formats: List[OutputFormat]
    
class ReportResponse(BaseModel):
    id: int
    name: str
    template_id: int
    state: ReportState
    created_at: datetime
    
    class Config:
        from_attributes = True

class ScheduleCreate(BaseModel):
    report_id: int
    cron_expression: str
    timezone: str = "UTC"
    
class DistributionListCreate(BaseModel):
    name: str
    recipients: List[Dict[str, str]]
    channels: List[str]

class ExecutionResponse(BaseModel):
    id: int
    report_id: int
    state: ReportState
    output_paths: Optional[Dict[str, str]]
    execution_time_ms: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
