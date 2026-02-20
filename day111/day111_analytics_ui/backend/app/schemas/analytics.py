from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class MetricSnapshotCreate(BaseModel):
    metric_name: str
    value: float
    unit: str = ""
    tags: dict = {}

class MetricSnapshotOut(BaseModel):
    id: int
    metric_name: str
    value: float
    unit: str
    tags: dict
    recorded_at: datetime
    model_config = {"from_attributes": True}

class DashboardKPI(BaseModel):
    name: str
    value: float
    unit: str
    trend: float
    trend_direction: str
    sparkline: list[float]

class DashboardResponse(BaseModel):
    kpis: list[DashboardKPI]
    updated_at: datetime

class MLPredictRequest(BaseModel):
    features: dict[str, float]
    model_name: str = "infra_anomaly"

class MLPredictResponse(BaseModel):
    prediction: str
    probability: float
    confidence: float
    feature_importance: dict[str, float]
    model_version: str

class CorrelationRequest(BaseModel):
    metrics: list[str]
    time_window_hours: int = Field(default=6, ge=1, le=168)
    method: str = Field(default="pearson", pattern="^(pearson|spearman)$")

class CorrelationResponse(BaseModel):
    matrix: list[list[float]]
    labels: list[str]
    method: str
    computed_at: datetime

class ReportCreate(BaseModel):
    name: str
    config: dict
    schedule_cron: str | None = None
    output_format: str = "pdf"
    is_template: bool = False

class ReportOut(BaseModel):
    id: int
    name: str
    config: dict
    schedule_cron: str | None
    output_format: str
    is_template: bool
    created_at: datetime
    last_run_at: datetime | None
    model_config = {"from_attributes": True}

class ConfigUpdate(BaseModel):
    key: str
    value: Any
