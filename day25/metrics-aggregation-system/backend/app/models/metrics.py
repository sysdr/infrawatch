from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List

class MetricData(BaseModel):
    """Raw metric data model"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AggregatedMetric(BaseModel):
    """Aggregated metric data model"""
    name: str
    aggregations: Dict[str, float]
    timestamp: datetime
    resolution: str  # e.g., "1m", "5m", "1h", "1d"
    tags: Dict[str, str] = {}
    sample_count: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MetricQuery(BaseModel):
    """Metric query model"""
    metric_name: str
    start_time: datetime
    end_time: datetime
    tags: Dict[str, str] = {}
    resolution: Optional[str] = None
    aggregation_type: str = "average"  # average, sum, min, max, count
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TrendAnalysis(BaseModel):
    """Trend analysis result model"""
    metric_name: str
    trend_direction: str  # "up", "down", "stable"
    change_percent: float
    confidence: float
    anomalies_detected: List[Dict[str, Any]] = []
    seasonality: Dict[str, Any] = {}
    
class AlertRule(BaseModel):
    """Alert rule model"""
    name: str
    metric_name: str
    condition: str  # "greater_than", "less_than", "outside_range"
    threshold: float
    secondary_threshold: Optional[float] = None
    tags: Dict[str, str] = {}
    enabled: bool = True
    notification_channels: List[str] = []
