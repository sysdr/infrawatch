from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MetricSampleIn(BaseModel):
    cpu_usage: float = Field(..., ge=0, le=100)
    memory_usage: float = Field(..., ge=0, le=100)
    request_rate: float = Field(..., ge=0)
    error_rate: float = Field(..., ge=0, le=100)
    latency_p99: float = Field(..., ge=0)
    disk_io: float = Field(..., ge=0)
    network_in: float = Field(..., ge=0)
    network_out: float = Field(..., ge=0)

class AnomalyResponse(BaseModel):
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool
    severity: str
    affected_metrics: List[str]
    description: str

class ForecastResponse(BaseModel):
    metric_name: str
    timestamps: List[str]
    forecast: List[float]
    lower_bound: List[float]
    upper_bound: List[float]
    rmse: Optional[float]

class PatternResponse(BaseModel):
    cluster_id: int
    cluster_label: str
    sample_count: int
    silhouette_score: float
    centroid: Dict[str, float]

class ModelEvaluation(BaseModel):
    model_type: str
    trained_at: Optional[datetime]
    training_samples: int
    anomaly_rate: float
    avg_anomaly_score: float
    forecast_rmse: float
    silhouette_score: float
    drift_score: float
    is_healthy: bool

class TrainResponse(BaseModel):
    status: str
    model_type: str
    training_samples: int
    metrics: Dict[str, Any]
    trained_at: str
