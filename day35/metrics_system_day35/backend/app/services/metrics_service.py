from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from typing import Dict

class MetricsService:
    def __init__(self):
        # Initialize Prometheus metrics
        self.task_counter = Counter('tasks_total', 'Total number of tasks', ['task_type', 'status'])
        self.task_duration = Histogram('task_duration_seconds', 'Task execution time', ['task_type'])
        self.active_tasks = Gauge('active_tasks', 'Number of active tasks')
        self.queue_size = Gauge('queue_size', 'Number of tasks in queue', ['priority'])
    
    def increment_task_counter(self, task_type: str, status: str):
        """Increment task counter"""
        self.task_counter.labels(task_type=task_type, status=status).inc()
    
    def record_task_duration(self, task_type: str, duration: float):
        """Record task execution duration"""
        self.task_duration.labels(task_type=task_type).observe(duration)
    
    def set_active_tasks(self, count: int):
        """Set number of active tasks"""
        self.active_tasks.set(count)
    
    def set_queue_size(self, priority: str, size: int):
        """Set queue size for priority"""
        self.queue_size.labels(priority=priority).set(size)
    
    def get_metrics(self) -> str:
        """Get Prometheus formatted metrics"""
        return generate_latest().decode('utf-8')
