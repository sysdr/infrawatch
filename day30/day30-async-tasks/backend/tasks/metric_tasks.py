from celery import Task
from config.celery_config import celery_app
from models.metric import Metric
from models.base import SessionLocal
import psutil
import time
import json
from datetime import datetime
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=2)

class CallbackTask(Task):
    """Base task with database session management"""
    def on_success(self, retval, task_id, args, kwargs):
        self.log_task_result(task_id, "success", retval)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.log_task_result(task_id, "failed", None, str(exc))
    
    def log_task_result(self, task_id, status, result=None, error=None):
        with SessionLocal() as db:
            from models.task_result import TaskResult
            task_result = TaskResult(
                task_id=task_id,
                task_name=self.name,
                status=status,
                result=result,
                error_message=error
            )
            db.add(task_result)
            db.commit()

@celery_app.task(base=CallbackTask, bind=True)
def collect_system_metrics(self):
    """Collect CPU, memory, and disk metrics"""
    try:
        # Gather system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics_data = [
            {
                "name": "cpu_usage_percent",
                "value": cpu_percent,
                "unit": "percent",
                "source": "system",
                "meta_data": {"cores": psutil.cpu_count()}
            },
            {
                "name": "memory_usage_percent", 
                "value": memory.percent,
                "unit": "percent",
                "source": "system",
                "meta_data": {"total_gb": round(memory.total / (1024**3), 2)}
            },
            {
                "name": "disk_usage_percent",
                "value": disk.percent,
                "unit": "percent", 
                "source": "system",
                "meta_data": {"total_gb": round(disk.total / (1024**3), 2)}
            }
        ]
        
        # Store in database
        with SessionLocal() as db:
            for metric_data in metrics_data:
                metric = Metric(**metric_data)
                db.add(metric)
            db.commit()
        
        # Store in Redis for real-time access
        redis_key = f"metrics:latest:{int(time.time())}"
        redis_client.setex(redis_key, 300, json.dumps(metrics_data))
        
        # Check thresholds and chain notification if needed
        for metric_data in metrics_data:
            if metric_data["value"] > 80:  # High usage threshold
                from tasks.notification_tasks import send_threshold_alert
                send_threshold_alert.delay(
                    metric_name=metric_data["name"],
                    value=metric_data["value"],
                    threshold=80
                )
        
        return {"metrics_collected": len(metrics_data), "timestamp": time.time()}
        
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(base=CallbackTask, bind=True)  
def collect_custom_metric(self, metric_name, value, unit, source="custom", tags=None):
    """Collect a custom metric"""
    try:
        with SessionLocal() as db:
            metric = Metric(
                name=metric_name,
                value=value,
                unit=unit,
                source=source,
                tags=tags or {},
                meta_data={"collection_time": time.time()}
            )
            db.add(metric)
            db.commit()
            
        # Cache in Redis
        metric_data = {
            "name": metric_name,
            "value": value,
            "unit": unit,
            "source": source,
            "timestamp": time.time()
        }
        redis_client.setex(f"metric:{metric_name}:latest", 300, json.dumps(metric_data))
        
        return {"metric": metric_name, "value": value}
        
    except Exception as e:
        self.retry(exc=e, countdown=30, max_retries=3)
