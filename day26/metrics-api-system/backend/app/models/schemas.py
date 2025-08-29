from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class AggregationType(str, Enum):
    avg = "avg"
    sum = "sum"
    count = "count"
    min = "min"
    max = "max"
    p50 = "p50"
    p95 = "p95"
    p99 = "p99"

class IntervalType(str, Enum):
    minute = "1m"
    five_minutes = "5m"
    fifteen_minutes = "15m"
    hour = "1h"
    day = "1d"
    week = "1w"

class ExportFormat(str, Enum):
    json = "json"
    csv = "csv"

class MetricQueryRequest(BaseModel):
    metric_name: str = Field(..., description="Name of the metric to query")
    start_time: datetime = Field(..., description="Start time for the query")
    end_time: datetime = Field(..., description="End time for the query")
    interval: IntervalType = Field(default=IntervalType.five_minutes, description="Time interval for aggregation")
    aggregations: List[AggregationType] = Field(default=[AggregationType.avg], description="List of aggregation types")
    tags: Optional[Dict[str, str]] = Field(None, description="Tag filters")
    limit: Optional[int] = Field(default=1000, ge=1, le=10000, description="Maximum number of data points")
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class MetricDataPoint(BaseModel):
    timestamp: datetime
    value: float
    aggregation_type: str

class MetricQueryResponse(BaseModel):
    metric_name: str
    start_time: datetime
    end_time: datetime
    interval: str
    data_points: List[MetricDataPoint]
    total_points: int
    cache_hit: bool = False

class ExportRequest(BaseModel):
    metric_name: str
    start_time: datetime
    end_time: datetime
    format: ExportFormat = ExportFormat.json
    aggregation: AggregationType = AggregationType.avg
    interval: IntervalType = IntervalType.five_minutes

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    cache: str
    version: str
