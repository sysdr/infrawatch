from celery import Celery
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "metrics_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_default_queue="default",
    task_routes={
        "process_metrics_task": {"queue": "default"},
        "process_csv_task": {"queue": "csv_processing"},
        "cleanup_task": {"queue": "maintenance"}
    }
)
