import time
from typing import Dict, List
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from prometheus_client.core import REGISTRY

class MetricsCollector:
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Task metrics
        self.task_counter = Counter(
            'tasks_total',
            'Total number of tasks',
            ['status', 'queue'],
            registry=self.registry
        )
        
        self.execution_time = Histogram(
            'task_execution_seconds',
            'Task execution time in seconds',
            ['queue'],
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'system_memory_usage_percent', 
            'System memory usage percentage',
            registry=self.registry
        )
        
        # Queue metrics
        self.queue_depth = Gauge(
            'queue_depth',
            'Current queue depth',
            ['queue'],
            registry=self.registry
        )
        
        # Worker metrics
        self.worker_count = Gauge(
            'workers_total',
            'Total number of workers',
            ['status'],
            registry=self.registry
        )
    
    async def initialize(self):
        """Initialize metrics collector"""
        pass
    
    def record_task_completion(self, status: str, queue: str, execution_time: float = None):
        """Record task completion metrics"""
        self.task_counter.labels(status=status, queue=queue).inc()
        
        if execution_time and status == 'completed':
            self.execution_time.labels(queue=queue).observe(execution_time)
    
    def record_gauge(self, metric_name: str, value: float, labels: Dict = None):
        """Record gauge metric"""
        if metric_name.startswith('system_cpu_usage'):
            self.cpu_usage.set(value)
        elif metric_name.startswith('system_memory_usage'):
            self.memory_usage.set(value)
        elif metric_name.startswith('queue_depth'):
            queue = labels.get('queue', 'default') if labels else 'default'
            self.queue_depth.labels(queue=queue).set(value)
    
    def get_metrics(self) -> str:
        """Get Prometheus formatted metrics"""
        return generate_latest(self.registry)
