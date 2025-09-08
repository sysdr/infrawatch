from celery import Task
from config.celery_config import celery_app
from models.base import SessionLocal
from models.metric import Metric
from models.task_result import TaskResult
from models.notification import Notification
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=5)

@celery_app.task(bind=True)
def cleanup_old_data(self, days_to_keep=7):
    """Clean up old metrics and task results"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        with SessionLocal() as db:
            # Clean old metrics
            old_metrics = db.query(Metric).filter(Metric.created_at < cutoff_date)
            metrics_count = old_metrics.count()
            old_metrics.delete(synchronize_session=False)
            
            # Clean old task results
            old_tasks = db.query(TaskResult).filter(TaskResult.created_at < cutoff_date)
            tasks_count = old_tasks.count()
            old_tasks.delete(synchronize_session=False)
            
            # Clean old notifications
            old_notifications = db.query(Notification).filter(Notification.created_at < cutoff_date)
            notifications_count = old_notifications.count()
            old_notifications.delete(synchronize_session=False)
            
            db.commit()
        
        # Clean Redis cache keys
        redis_keys_cleaned = 0
        for db_num in range(6):  # Check all Redis databases
            r = redis.Redis(host='localhost', port=6379, db=db_num)
            keys = r.keys("*")
            for key in keys:
                ttl = r.ttl(key)
                if ttl == -1:  # Keys without expiration
                    r.expire(key, 86400)  # Set 24-hour expiration
                    redis_keys_cleaned += 1
        
        cleanup_result = {
            "metrics_deleted": metrics_count,
            "tasks_deleted": tasks_count,
            "notifications_deleted": notifications_count,
            "redis_keys_updated": redis_keys_cleaned,
            "cleanup_date": cutoff_date.isoformat()
        }
        
        return cleanup_result
        
    except Exception as e:
        self.retry(exc=e, countdown=600, max_retries=2)

@celery_app.task(bind=True)
def optimize_database(self):
    """Optimize database performance"""
    try:
        with SessionLocal() as db:
            # PostgreSQL-specific optimization
            db.execute("VACUUM ANALYZE metrics")
            db.execute("VACUUM ANALYZE task_results") 
            db.execute("VACUUM ANALYZE notifications")
            db.commit()
        
        # Update statistics
        optimization_result = {
            "vacuum_completed": True,
            "analyze_completed": True,
            "optimized_at": datetime.utcnow().isoformat()
        }
        
        return optimization_result
        
    except Exception as e:
        self.retry(exc=e, countdown=1800, max_retries=1)

@celery_app.task(bind=True)
def health_check_system(self):
    """Perform system health check"""
    try:
        health_status = {}
        
        # Check database connection
        try:
            with SessionLocal() as db:
                db.execute("SELECT 1")
            health_status["database"] = "healthy"
        except Exception:
            health_status["database"] = "unhealthy"
        
        # Check Redis connection
        try:
            redis_client.ping()
            health_status["redis"] = "healthy"
        except Exception:
            health_status["redis"] = "unhealthy"
        
        # Check recent task execution
        try:
            with SessionLocal() as db:
                recent_time = datetime.utcnow() - timedelta(minutes=10)
                recent_tasks = db.query(TaskResult).filter(
                    TaskResult.created_at >= recent_time
                ).count()
            health_status["task_queue"] = "healthy" if recent_tasks > 0 else "idle"
        except Exception:
            health_status["task_queue"] = "unhealthy"
        
        # Overall system status
        unhealthy_components = [k for k, v in health_status.items() if v == "unhealthy"]
        health_status["overall"] = "unhealthy" if unhealthy_components else "healthy"
        health_status["checked_at"] = datetime.utcnow().isoformat()
        
        # Cache health status
        redis_client.setex("system:health", 300, str(health_status))
        
        return health_status
        
    except Exception as e:
        self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True)
def archive_old_reports(self, days_to_keep=30):
    """Archive old report data"""
    try:
        cutoff_timestamp = (datetime.utcnow() - timedelta(days=days_to_keep)).timestamp()
        
        archived_reports = 0
        # Check all report keys in Redis
        for db_num in range(6):
            r = redis.Redis(host='localhost', port=6379, db=db_num)
            report_keys = r.keys("report:*")
            
            for key in report_keys:
                try:
                    # Extract timestamp from key
                    timestamp_part = key.decode().split(":")[-1]
                    report_timestamp = float(timestamp_part)
                    
                    if report_timestamp < cutoff_timestamp:
                        # Archive to a compressed format or delete
                        r.delete(key)
                        archived_reports += 1
                except (ValueError, IndexError):
                    continue  # Skip malformed keys
        
        return {
            "reports_archived": archived_reports,
            "cutoff_date": datetime.fromtimestamp(cutoff_timestamp).isoformat()
        }
        
    except Exception as e:
        self.retry(exc=e, countdown=900, max_retries=1)
