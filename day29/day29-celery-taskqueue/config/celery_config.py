from kombu import Queue

# Celery Configuration
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

timezone = 'UTC'
enable_utc = True

# Task routing
task_routes = {
    'app.tasks.collect_metrics': {'queue': 'metrics.high'},
    'app.tasks.process_data': {'queue': 'metrics.normal'},
    'app.tasks.send_notification': {'queue': 'notifications.urgent'},
    'app.tasks.generate_report': {'queue': 'reports.background'},
}

# Queue definitions
task_queues = (
    Queue('metrics.high', routing_key='metrics.high'),
    Queue('metrics.normal', routing_key='metrics.normal'),
    Queue('notifications.urgent', routing_key='notifications.urgent'),
    Queue('reports.background', routing_key='reports.background'),
)

# Worker configuration
worker_prefetch_multiplier = 1
task_acks_late = True
worker_max_tasks_per_child = 1000

# Task execution settings
task_soft_time_limit = 300  # 5 minutes
task_time_limit = 600       # 10 minutes

# Rate limiting
task_annotations = {
    'app.tasks.collect_metrics': {'rate_limit': '100/m'},
    'app.tasks.generate_report': {'rate_limit': '10/m'},
}
