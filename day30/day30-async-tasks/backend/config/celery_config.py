from celery import Celery
import os

# Celery configuration
celery_app = Celery(
    "metrics_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    include=["tasks.metric_tasks", "tasks.notification_tasks", "tasks.report_tasks", "tasks.maintenance_tasks"]
)

# Task routing
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "tasks.metric_tasks.*": {"queue": "metrics"},
        "tasks.notification_tasks.*": {"queue": "notifications"},
        "tasks.report_tasks.*": {"queue": "reports"},
        "tasks.maintenance_tasks.*": {"queue": "maintenance"},
    },
    task_default_retry_delay=60,
    task_max_retries=3,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression="gzip",
    result_compression="gzip",
    result_expires=3600,
)

# Task scheduling
celery_app.conf.beat_schedule = {
    "collect-system-metrics": {
        "task": "tasks.metric_tasks.collect_system_metrics",
        "schedule": 30.0,  # Every 30 seconds
    },
    "cleanup-old-data": {
        "task": "tasks.maintenance_tasks.cleanup_old_data",
        "schedule": 3600.0,  # Every hour
    },
}
