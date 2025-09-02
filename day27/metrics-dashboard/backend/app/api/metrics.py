from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json
from ..models.metrics import get_db, MetricData

router = APIRouter()

@router.get("/metrics")
async def get_metrics(
    metric_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(default=1000, le=10000),
    db: Session = Depends(get_db)
):
    """Get metrics data with optional filtering"""
    query = db.query(MetricData)
    
    if metric_name:
        query = query.filter(MetricData.metric_name == metric_name)
    
    if start_time:
        query = query.filter(MetricData.timestamp >= start_time)
    
    if end_time:
        query = query.filter(MetricData.timestamp <= end_time)
    
    query = query.order_by(MetricData.timestamp.desc()).limit(limit)
    results = query.all()
    
    return [metric.to_dict() for metric in results]

@router.get("/metrics/names")
async def get_metric_names(db: Session = Depends(get_db)):
    """Get list of available metric names"""
    names = db.query(MetricData.metric_name).distinct().all()
    return [name[0] for name in names]

@router.post("/metrics")
async def create_metric(
    metric_name: str,
    value: float,
    labels: dict = {},
    db: Session = Depends(get_db)
):
    """Create new metric data point"""
    metric = MetricData(
        metric_name=metric_name,
        value=value,
        labels=json.dumps(labels)
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric.to_dict()
