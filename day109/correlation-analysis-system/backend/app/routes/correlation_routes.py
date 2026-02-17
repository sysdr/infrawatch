from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from models.database import get_db, Metric, MetricData, Correlation, CausalRelation, ImpactAssessment
from services.correlation_engine import CorrelationEngine
from services.root_cause_analyzer import RootCauseAnalyzer
from services.impact_assessor import ImpactAssessor
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import numpy as np

router = APIRouter(prefix="/api/correlation", tags=["correlation"])


class MetricCreate(BaseModel):
    name: str
    service: str
    metric_type: str
    tags: Optional[Dict[str, Any]] = {}


class MetricDataCreate(BaseModel):
    metric_id: int
    value: float
    timestamp: Optional[datetime] = None


@router.post("/metrics")
def create_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    """Create a new metric"""
    db_metric = Metric(**metric.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.post("/metrics/data")
def add_metric_data(data: MetricDataCreate, db: Session = Depends(get_db)):
    """Add data point for a metric"""
    if data.timestamp is None:
        data.timestamp = datetime.utcnow()
    
    db_data = MetricData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


@router.post("/metrics/generate-sample")
def generate_sample_metrics(db: Session = Depends(get_db)):
    """Generate sample metrics and data for demonstration"""
    
    # Create sample metrics
    metrics_config = [
        {"name": "api.latency", "service": "api-gateway", "metric_type": "gauge"},
        {"name": "db.connections", "service": "database", "metric_type": "gauge"},
        {"name": "db.query_time", "service": "database", "metric_type": "gauge"},
        {"name": "cache.hit_rate", "service": "cache", "metric_type": "gauge"},
        {"name": "cpu.usage", "service": "app-server", "metric_type": "gauge"},
        {"name": "memory.usage", "service": "app-server", "metric_type": "gauge"},
        {"name": "request.rate", "service": "api-gateway", "metric_type": "counter"},
        {"name": "error.rate", "service": "api-gateway", "metric_type": "counter"},
    ]
    
    created_metrics = []
    for config in metrics_config:
        existing = db.query(Metric).filter(Metric.name == config["name"]).first()
        if not existing:
            metric = Metric(**config, tags={})
            db.add(metric)
            db.commit()
            db.refresh(metric)
            created_metrics.append(metric)
        else:
            created_metrics.append(existing)
    
    # Generate correlated time-series data
    base_time = datetime.utcnow() - timedelta(hours=2)
    
    for i in range(120):  # 2 hours of minute-level data
        timestamp = base_time + timedelta(minutes=i)
        
        # Base pattern
        base_load = 50 + 30 * np.sin(i / 20)  # Simulated daily pattern
        noise = random.gauss(0, 5)
        
        # Generate correlated values
        api_latency = base_load + noise + random.gauss(0, 3)
        db_connections = base_load * 1.2 + noise + random.gauss(0, 4)
        db_query_time = db_connections * 0.8 + random.gauss(0, 3)
        cache_hit_rate = 95 - (base_load * 0.3) + random.gauss(0, 2)
        cpu_usage = base_load * 0.9 + random.gauss(0, 4)
        memory_usage = cpu_usage * 1.1 + random.gauss(0, 3)
        request_rate = 1000 + base_load * 10 + random.gauss(0, 50)
        error_rate = max(0, (api_latency - 50) * 0.5 + random.gauss(0, 2))
        
        data_values = [
            api_latency, db_connections, db_query_time, cache_hit_rate,
            cpu_usage, memory_usage, request_rate, error_rate
        ]
        
        for metric, value in zip(created_metrics, data_values):
            data_point = MetricData(
                metric_id=metric.id,
                timestamp=timestamp,
                value=max(0, value)
            )
            db.add(data_point)
    
    db.commit()
    
    return {
        "message": "Sample metrics and data generated",
        "metrics_created": len(created_metrics),
        "data_points": 120 * len(created_metrics)
    }


@router.post("/detect")
def detect_correlations(background_tasks: BackgroundTasks):
    """Trigger correlation detection"""
    engine = CorrelationEngine(window_minutes=30, threshold=0.7)
    correlations = engine.detect_correlations()
    return {
        "status": "completed",
        "correlations_detected": len(correlations),
        "correlations": correlations
    }


@router.get("/correlations")
def get_correlations(state: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all correlations"""
    query = db.query(Correlation)
    
    if state:
        query = query.filter(Correlation.state == state)
    
    correlations = query.order_by(Correlation.detected_at.desc()).all()
    
    # Enrich with metric names
    result = []
    for corr in correlations:
        metric_a = db.query(Metric).filter(Metric.id == corr.metric_a_id).first()
        metric_b = db.query(Metric).filter(Metric.id == corr.metric_b_id).first()
        
        result.append({
            "id": corr.id,
            "metric_a": {"id": corr.metric_a_id, "name": metric_a.name if metric_a else "Unknown"},
            "metric_b": {"id": corr.metric_b_id, "name": metric_b.name if metric_b else "Unknown"},
            "coefficient": corr.coefficient,
            "correlation_type": corr.correlation_type,
            "p_value": corr.p_value,
            "state": corr.state,
            "lag_seconds": corr.lag_seconds,
            "detected_at": corr.detected_at.isoformat(),
            "last_updated": corr.last_updated.isoformat()
        })
    
    return result


@router.post("/analyze/root-cause")
def analyze_root_cause():
    """Perform root cause analysis"""
    analyzer = RootCauseAnalyzer()
    causal_graph = analyzer.build_causal_graph(lookback_minutes=60)
    root_causes = analyzer.find_root_causes(causal_graph)
    
    return {
        "status": "completed",
        "causal_edges": sum(len(v) for v in causal_graph.values()),
        "root_causes": root_causes,
        "causal_graph": {str(k): [(e[0], e[1]) for e in v] for k, v in causal_graph.items()}
    }


@router.post("/analyze/impact/{metric_id}")
def analyze_impact(metric_id: int, db: Session = Depends(get_db)):
    """Assess impact from a specific metric"""
    # Build causal graph first
    analyzer = RootCauseAnalyzer()
    causal_graph = analyzer.build_causal_graph(lookback_minutes=60)
    
    # Assess impact
    assessor = ImpactAssessor()
    impact = assessor.assess_impact(metric_id, causal_graph)
    
    return impact


@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get summary stats for dashboard"""
    total_metrics = db.query(Metric).count()
    active_correlations = db.query(Correlation).filter(Correlation.state == "active").count()
    total_correlations = db.query(Correlation).count()
    
    # Get recent root causes
    analyzer = RootCauseAnalyzer()
    causal_graph = analyzer.build_causal_graph(lookback_minutes=60)
    root_causes = analyzer.find_root_causes(causal_graph)
    
    return {
        "total_metrics": total_metrics,
        "active_correlations": active_correlations,
        "total_correlations": total_correlations,
        "root_causes_identified": len(root_causes),
        "recent_root_causes": root_causes[:5]
    }
