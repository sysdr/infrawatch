from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from services.metrics_service import MetricsService
from config.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

class MetricRequest(BaseModel):
    metric_name: str
    metric_type: str = "gauge"
    value: float
    timestamp: Optional[datetime] = None
    tags: Dict[str, str] = {}
    labels: Dict[str, str] = {}

class MetricQuery(BaseModel):
    metric_name: str
    start_time: datetime
    end_time: datetime
    tags: Optional[Dict[str, str]] = None
    interval: Optional[str] = None

@router.post("/store")
async def store_metric(metric: MetricRequest, db: Session = Depends(get_db)):
    """Store a single metric"""
    
    service = MetricsService(db)
    
    metric_data = {
        'metric_name': metric.metric_name,
        'metric_type': metric.metric_type,
        'value': metric.value,
        'timestamp': metric.timestamp or datetime.now(timezone.utc),
        'tags': metric.tags,
        'labels': metric.labels
    }
    
    metric_id = service.store_metric(metric_data)
    db.commit()
    
    return {"metric_id": metric_id, "status": "stored"}

@router.post("/batch-store")
async def batch_store_metrics(metrics: List[MetricRequest], db: Session = Depends(get_db)):
    """Store multiple metrics efficiently"""
    
    service = MetricsService(db)
    
    metrics_data = []
    for metric in metrics:
        metrics_data.append({
            'metric_name': metric.metric_name,
            'metric_type': metric.metric_type,
            'value': metric.value,
            'timestamp': metric.timestamp or datetime.now(timezone.utc),
            'tags': metric.tags,
            'labels': metric.labels
        })
    
    metric_ids = service.batch_store_metrics(metrics_data)
    db.commit()
    
    return {"metric_ids": metric_ids, "count": len(metric_ids), "status": "stored"}

@router.get("/query")
async def query_metrics(
    metric_name: str,
    start_time: datetime,
    end_time: datetime,
    tags: str = Query(None, description="JSON string of tags"),
    db: Session = Depends(get_db)
):
    """Query metrics with time range and filters"""
    
    service = MetricsService(db)
    
    tag_dict = {}
    if tags:
        import json
        tag_dict = json.loads(tags)
    
    results = service.query_metrics(metric_name, start_time, end_time, tag_dict)
    
    return {
        "metric_name": metric_name,
        "data_points": len(results),
        "data": results
    }

@router.get("/aggregated")
async def get_aggregated_metrics(
    metric_name: str,
    interval: str,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db)
):
    """Get pre-computed aggregations"""
    
    service = MetricsService(db)
    results = service.get_aggregated_metrics(metric_name, interval, start_time, end_time)
    
    return {
        "metric_name": metric_name,
        "interval": interval,
        "data_points": len(results),
        "data": results
    }

@router.get("/search")
async def search_metrics(
    q: str = Query(..., description="Search term"),
    limit: int = Query(50, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search for metrics"""
    
    service = MetricsService(db)
    results = service.search_metrics(q, limit)
    
    return {"results": results, "count": len(results)}

@router.post("/aggregate/{interval}")
async def create_aggregations(interval: str, db: Session = Depends(get_db)):
    """Trigger aggregation creation"""
    
    service = MetricsService(db)
    service.create_aggregations(interval)
    db.commit()
    
    return {"status": "aggregations created", "interval": interval}
