from celery import Celery
import os
from kombu import Queue

def make_celery():
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    celery = Celery(
        'tasks',
        broker=broker_url,
        backend=result_backend,
        include=['app.tasks']
    )
    
    # Configure queues
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_routes={
            'app.tasks.collect_metrics': {'queue': 'metrics.high'},
            'app.tasks.generate_report': {'queue': 'reports.background'},
            'app.tasks.send_notification': {'queue': 'notifications.urgent'},
            'app.tasks.process_data': {'queue': 'metrics.normal'},
        },
        task_default_queue='default',
        task_queues=(
            Queue('metrics.high', routing_key='metrics.high'),
            Queue('metrics.normal', routing_key='metrics.normal'),
            Queue('notifications.urgent', routing_key='notifications.urgent'),
            Queue('reports.background', routing_key='reports.background'),
            Queue('default', routing_key='default'),
        ),
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
        task_soft_time_limit=300,
        task_time_limit=600,
        task_annotations={
            'app.tasks.collect_metrics': {'rate_limit': '100/m'},
            'app.tasks.generate_report': {'rate_limit': '10/m'},
        }
    )
    
    return celery

celery_app = make_celery()
