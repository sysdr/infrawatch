from celery import Task
from config.celery_config import celery_app
from models.metric import Metric
from models.base import SessionLocal
import json
import time
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=4)

@celery_app.task(bind=True)
def generate_hourly_report(self, metric_names=None):
    """Generate hourly metrics report"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        with SessionLocal() as db:
            query = db.query(Metric).filter(
                Metric.created_at >= start_time,
                Metric.created_at <= end_time
            )
            
            if metric_names:
                query = query.filter(Metric.name.in_(metric_names))
            
            metrics = query.all()
        
        # Process metrics data
        report_data = {}
        for metric in metrics:
            name = metric.name
            if name not in report_data:
                report_data[name] = {
                    "values": [],
                    "avg": 0,
                    "min": float('inf'),
                    "max": float('-inf'),
                    "count": 0,
                    "unit": metric.unit
                }
            
            report_data[name]["values"].append(metric.value)
            report_data[name]["min"] = min(report_data[name]["min"], metric.value)
            report_data[name]["max"] = max(report_data[name]["max"], metric.value)
            report_data[name]["count"] += 1
        
        # Calculate averages
        for name, data in report_data.items():
            if data["values"]:
                data["avg"] = sum(data["values"]) / len(data["values"])
            del data["values"]  # Remove raw values to save space
        
        report = {
            "report_type": "hourly",
            "period": {"start": start_time.isoformat(), "end": end_time.isoformat()},
            "metrics": report_data,
            "generated_at": time.time()
        }
        
        # Cache report
        report_key = f"report:hourly:{int(start_time.timestamp())}"
        redis_client.setex(report_key, 7200, json.dumps(report))  # Cache for 2 hours
        
        return {"report_id": report_key, "metrics_count": len(report_data)}
        
    except Exception as e:
        self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True)
def generate_dashboard_summary(self):
    """Generate real-time dashboard summary"""
    try:
        with SessionLocal() as db:
            # Get latest metrics (last 5 minutes)
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            recent_metrics = db.query(Metric).filter(
                Metric.created_at >= recent_time
            ).all()
        
        # Group by metric name
        summary = {}
        for metric in recent_metrics:
            name = metric.name
            if name not in summary:
                summary[name] = {
                    "current": metric.value,
                    "unit": metric.unit,
                    "last_updated": metric.created_at.isoformat(),
                    "source": metric.source,
                    "status": "normal"
                }
            
            # Keep most recent value
            if metric.created_at > datetime.fromisoformat(summary[name]["last_updated"].replace('Z', '+00:00')):
                summary[name]["current"] = metric.value
                summary[name]["last_updated"] = metric.created_at.isoformat()
            
            # Set status based on thresholds
            if metric.value > 90:
                summary[name]["status"] = "critical"
            elif metric.value > 75:
                summary[name]["status"] = "warning"
        
        dashboard_data = {
            "summary": summary,
            "total_metrics": len(summary),
            "last_updated": datetime.utcnow().isoformat(),
            "status": "healthy" if not any(s["status"] == "critical" for s in summary.values()) else "alert"
        }
        
        # Cache for dashboard
        redis_client.setex("dashboard:summary", 30, json.dumps(dashboard_data))
        
        return dashboard_data
        
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def generate_trend_analysis(self, metric_name, hours=24):
    """Generate trend analysis for a specific metric"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        with SessionLocal() as db:
            metrics = db.query(Metric).filter(
                Metric.name == metric_name,
                Metric.created_at >= start_time,
                Metric.created_at <= end_time
            ).order_by(Metric.created_at).all()
        
        if not metrics:
            return {"error": "No data found for metric", "metric": metric_name}
        
        # Calculate trend
        values = [m.value for m in metrics]
        timestamps = [m.created_at.timestamp() for m in metrics]
        
        # Simple linear trend calculation
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        trend_analysis = {
            "metric_name": metric_name,
            "period_hours": hours,
            "data_points": n,
            "current_value": values[-1],
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": sum(values) / n,
            "trend_slope": slope,
            "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "generated_at": time.time()
        }
        
        # Cache analysis
        analysis_key = f"analysis:trend:{metric_name}:{hours}h"
        redis_client.setex(analysis_key, 1800, json.dumps(trend_analysis))  # Cache for 30 minutes
        
        return trend_analysis
        
    except Exception as e:
        self.retry(exc=e, countdown=180, max_retries=2)
