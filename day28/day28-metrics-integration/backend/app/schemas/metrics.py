from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any
import json

class MetricCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    value: float
    tags: Optional[Dict[str, Any]] = None
    source: str = Field(..., min_length=1, max_length=100)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Metric name must be alphanumeric with dots and underscores')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(json.dumps(v)) > 1000:
            raise ValueError('Tags JSON must be under 1000 characters')
        return v

class MetricResponse(BaseModel):
    id: int
    name: str
    value: float
    timestamp: datetime
    tags: Optional[str]
    source: str
    
    class Config:
        from_attributes = True

class MetricBatch(BaseModel):
    metrics: list[MetricCreate] = Field(..., max_items=1000)

class MetricQuery(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    database: bool
    redis: bool
    version: str = "1.0.0"
