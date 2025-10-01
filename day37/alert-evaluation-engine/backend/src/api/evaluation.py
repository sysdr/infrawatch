from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import redis.asyncio as redis
from datetime import datetime, timedelta
import random
import asyncio

from ..models.alert_rule import AlertRule, AlertInstance, AlertRuleCreate, AlertRuleResponse, RuleType, AlertSeverity
from ..services.rule_evaluator import EvaluationEngine, MetricPoint, EvaluationResult
from ..services.alert_generator import AlertGenerator

router = APIRouter()

# In-memory storage for demo purposes
rules_storage = [
    {
        "id": 1,
        "name": "High CPU Usage",
        "description": "CPU usage exceeds 80%",
        "metric_name": "cpu_usage_percent",
        "rule_type": RuleType.THRESHOLD,
        "conditions": {"greater_than": 80.0},
        "severity": AlertSeverity.WARNING,
        "evaluation_interval": 30,
        "for_duration": 300,
        "labels": {"service": "web", "team": "platform"},
        "annotations": {"runbook": "https://wiki.company.com/cpu-high"},
        "enabled": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": 2,
        "name": "Memory Anomaly Detection",
        "description": "Detects unusual memory usage patterns",
        "metric_name": "memory_usage_bytes",
        "rule_type": RuleType.ANOMALY,
        "conditions": {"type": "statistical", "z_threshold": 3.0},
        "severity": AlertSeverity.CRITICAL,
        "evaluation_interval": 60,
        "for_duration": 0,
        "labels": {"service": "database", "team": "data"},
        "annotations": {"description": "Statistical anomaly in memory usage"},
        "enabled": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Mock dependencies - in real app these would be proper dependency injection
async def get_redis():
    return redis.from_url("redis://localhost:6379", decode_responses=True)

async def get_db():
    # Mock database session
    return None

async def get_evaluation_engine():
    redis_client = await get_redis()
    return EvaluationEngine(redis_client)

@router.post("/rules", response_model=AlertRuleResponse)
async def create_alert_rule(rule: AlertRuleCreate, db: AsyncSession = Depends(get_db)):
    """Create new alert rule."""
    # Generate new ID
    new_id = max([r["id"] for r in rules_storage], default=0) + 1
    
    # Create new rule
    new_rule = {
        "id": new_id,
        "name": rule.name,
        "description": rule.description,
        "metric_name": rule.metric_name,
        "rule_type": rule.rule_type,
        "conditions": rule.conditions,
        "severity": rule.severity,
        "evaluation_interval": rule.evaluation_interval,
        "for_duration": rule.for_duration,
        "labels": rule.labels,
        "annotations": rule.annotations,
        "enabled": rule.enabled,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Add to storage
    rules_storage.append(new_rule)
    
    return AlertRuleResponse(**new_rule)

@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(db: AsyncSession = Depends(get_db)):
    """List all alert rules."""
    # Return rules from storage
    return [AlertRuleResponse(**rule) for rule in rules_storage]

@router.post("/evaluate")
async def manual_evaluation(
    background_tasks: BackgroundTasks,
    engine: EvaluationEngine = Depends(get_evaluation_engine)
):
    """Trigger manual rule evaluation."""
    # Simulate evaluation with mock data
    mock_metric = MetricPoint(
        timestamp=datetime.utcnow(),
        value=85.5,
        labels={"instance": "web-01", "region": "us-west-2"}
    )
    
    # Create mock historical data
    historical_data = []
    for i in range(100):
        historical_data.append(MetricPoint(
            timestamp=datetime.utcnow() - timedelta(minutes=i),
            value=random.uniform(60, 75),
            labels={"instance": "web-01", "region": "us-west-2"}
        ))
    
    return {
        "status": "evaluation_triggered",
        "timestamp": datetime.utcnow(),
        "metrics_evaluated": 1,
        "rules_processed": 2
    }

@router.get("/alerts/active")
async def get_active_alerts():
    """Get currently active alerts."""
    # Return sample active alerts
    active_alerts = [
        {
            "id": 1001,
            "rule_id": 1,
            "rule_name": "High CPU Usage",
            "state": "FIRING",
            "severity": "WARNING",
            "value": 85.5,
            "message": "CPU usage 85.5% exceeds threshold 80%",
            "labels": {"instance": "web-01", "service": "web"},
            "starts_at": datetime.utcnow() - timedelta(minutes=5),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 1002,
            "rule_id": 2,
            "rule_name": "Memory Anomaly Detection",
            "state": "FIRING",
            "severity": "CRITICAL",
            "value": 8.5e9,
            "message": "Statistical anomaly detected: Z-score 3.2 > 3.0",
            "labels": {"instance": "db-01", "service": "database"},
            "starts_at": datetime.utcnow() - timedelta(minutes=15),
            "updated_at": datetime.utcnow()
        }
    ]
    return active_alerts

@router.get("/metrics/evaluation")
async def get_evaluation_metrics():
    """Get evaluation engine metrics."""
    return {
        "rules_evaluated_per_second": random.uniform(50, 100),
        "evaluation_latency_ms": random.uniform(10, 50),
        "alerts_generated_last_hour": random.randint(5, 25),
        "false_positive_rate": random.uniform(0.02, 0.08),
        "deduplication_rate": random.uniform(0.15, 0.35),
        "anomaly_detection_accuracy": random.uniform(0.85, 0.95),
        "last_evaluation": datetime.utcnow(),
        "engine_status": "running"
    }

@router.post("/test-anomaly")
async def test_anomaly_detection():
    """Test anomaly detection algorithms."""
    # Generate test data with anomaly
    normal_data = [random.uniform(45, 55) for _ in range(100)]
    anomaly_data = normal_data + [85.0]  # Clear anomaly
    
    # Simulate Z-score calculation
    import numpy as np
    mean = np.mean(normal_data)
    std = np.std(normal_data)
    z_score = abs(85.0 - mean) / std
    
    return {
        "test_data_points": len(normal_data),
        "anomaly_value": 85.0,
        "normal_mean": round(mean, 2),
        "normal_std": round(std, 2),
        "z_score": round(z_score, 2),
        "anomaly_detected": z_score > 3.0,
        "detection_method": "statistical_z_score"
    }
