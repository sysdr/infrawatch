from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.base import SessionLocal, engine
from models import Base, Metric, TaskResult, Notification
from tasks import metric_tasks, notification_tasks, report_tasks, maintenance_tasks, task_chains
from config.celery_config import celery_app
import redis
import json
from datetime import datetime, timedelta
from typing import List, Optional
import psutil

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Metrics Collection API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Metrics Collection System API", "status": "running"}

@app.get("/health")
async def health_check():
    """System health check"""
    try:
        # Check database
        with SessionLocal() as db:
            db.execute("SELECT 1")
        
        # Check Redis
        redis_client.ping()
        
        # Check Celery
        celery_stats = celery_app.control.inspect().stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected", 
            "celery_workers": len(celery_stats) if celery_stats else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/metrics/collect")
async def trigger_metric_collection():
    """Trigger manual metric collection"""
    task = metric_tasks.collect_system_metrics.delay()
    return {"task_id": task.id, "status": "queued"}

@app.post("/metrics/custom")
async def collect_custom_metric(metric_name: str, value: float, unit: str = "count"):
    """Collect a custom metric"""
    task = metric_tasks.collect_custom_metric.delay(metric_name, value, unit)
    return {"task_id": task.id, "metric": metric_name, "value": value}

@app.get("/metrics/latest")
async def get_latest_metrics():
    """Get latest metrics from Redis cache"""
    try:
        dashboard_data = redis_client.get("dashboard:summary")
        if dashboard_data:
            return json.loads(dashboard_data)
        
        # Fallback to database
        with SessionLocal() as db:
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            metrics = db.query(Metric).filter(Metric.created_at >= recent_time).all()
            
        return {"metrics": [{"name": m.name, "value": m.value, "unit": m.unit} for m in metrics]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/history/{metric_name}")
async def get_metric_history(metric_name: str, hours: int = 24, db: Session = Depends(get_db)):
    """Get metric history"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    metrics = db.query(Metric).filter(
        Metric.name == metric_name,
        Metric.created_at >= start_time
    ).order_by(Metric.created_at).all()
    
    return {
        "metric_name": metric_name,
        "data_points": len(metrics),
        "data": [
            {
                "timestamp": m.created_at.isoformat(),
                "value": m.value,
                "unit": m.unit
            } for m in metrics
        ]
    }

@app.post("/reports/generate")
async def generate_report(report_type: str = "hourly"):
    """Generate a report"""
    if report_type == "hourly":
        task = report_tasks.generate_hourly_report.delay()
    elif report_type == "dashboard":
        task = report_tasks.generate_dashboard_summary.delay()
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    return {"task_id": task.id, "report_type": report_type}

@app.post("/notifications/test")
async def test_notification(channel: str = "slack", message: str = "Test notification"):
    """Send test notification"""
    if channel == "email":
        task = notification_tasks.send_email_notification.delay("Test", message, "test@example.com")
    elif channel == "slack":
        task = notification_tasks.send_slack_notification.delay(message, "#test")
    elif channel == "webhook":
        task = notification_tasks.send_webhook_notification.delay(
            "http://localhost:8000/webhook/test",
            {"message": message, "test": True}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid channel")
    
    return {"task_id": task.id, "channel": channel}

@app.post("/maintenance/run")
async def run_maintenance():
    """Run maintenance workflow"""
    task = task_chains.create_maintenance_workflow.delay()
    return {"task_id": task.id, "type": "maintenance_workflow"}

@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get task status"""
    task_result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "traceback": task_result.traceback if task_result.failed() else None
    }

@app.get("/tasks/active")
async def get_active_tasks():
    """Get active tasks"""
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    
    return {"active_tasks": active_tasks}

@app.post("/webhook/alert")
async def webhook_alert_handler(payload: dict):
    """Handle webhook alerts"""
    print(f"Webhook alert received: {payload}")
    return {"status": "received", "payload": payload}

@app.post("/webhook/test")
async def webhook_test_handler(payload: dict):
    """Handle test webhooks"""
    print(f"Test webhook received: {payload}")
    return {"status": "test_received", "payload": payload}

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        with SessionLocal() as db:
            # Get counts
            total_metrics = db.query(Metric).count()
            total_tasks = db.query(TaskResult).count()
            total_notifications = db.query(Notification).count()
            
            # Get recent activity
            recent_time = datetime.utcnow() - timedelta(hours=1)
            recent_metrics = db.query(Metric).filter(Metric.created_at >= recent_time).count()
            recent_tasks = db.query(TaskResult).filter(TaskResult.created_at >= recent_time).count()
        
        # Get system metrics
        system_stats = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        return {
            "totals": {
                "metrics": total_metrics,
                "tasks": total_tasks,
                "notifications": total_notifications
            },
            "recent_activity": {
                "metrics_last_hour": recent_metrics,
                "tasks_last_hour": recent_tasks
            },
            "system": system_stats,
            "updated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
