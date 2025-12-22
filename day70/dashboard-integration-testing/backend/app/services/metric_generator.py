import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio

class MetricGenerator:
    def __init__(self):
        self.history: List[Dict] = []
        self.max_history = 10000
        self.load_level = 'normal'
        self.start_time = time.time()
        self.total_metrics = 0
        
        # Metric types with different characteristics
        self.metric_types = [
            {'name': 'cpu_usage', 'min': 0, 'max': 100, 'volatility': 0.1},
            {'name': 'memory_usage', 'min': 0, 'max': 100, 'volatility': 0.05},
            {'name': 'disk_io', 'min': 0, 'max': 1000, 'volatility': 0.3},
            {'name': 'network_throughput', 'min': 0, 'max': 10000, 'volatility': 0.4},
            {'name': 'request_latency', 'min': 10, 'max': 500, 'volatility': 0.2},
            {'name': 'error_rate', 'min': 0, 'max': 10, 'volatility': 0.15},
        ]
        
        self.current_values = {m['name']: (m['min'] + m['max']) / 2 for m in self.metric_types}
        
    def set_load_level(self, level: str):
        """Set load simulation level: normal, high, burst"""
        self.load_level = level
        
    async def generate_batch(self, size: int = 10) -> List[Dict]:
        """Generate a batch of metrics"""
        metrics = []
        
        # Adjust batch size based on load level
        if self.load_level == 'high':
            size *= 10
        elif self.load_level == 'burst':
            size *= 100
            
        for _ in range(size):
            metric = self._generate_single_metric()
            metrics.append(metric)
            
            # Add to history
            self.history.append(metric)
            if len(self.history) > self.max_history:
                self.history.pop(0)
                
            self.total_metrics += 1
            
        return metrics
        
    def _generate_single_metric(self) -> Dict:
        """Generate a single metric data point"""
        metric_type = random.choice(self.metric_types)
        name = metric_type['name']
        
        # Random walk with mean reversion
        current = self.current_values[name]
        mean = (metric_type['min'] + metric_type['max']) / 2
        volatility = metric_type['volatility']
        
        # Mean reversion + random shock
        change = -0.1 * (current - mean) + random.gauss(0, volatility * (metric_type['max'] - metric_type['min']))
        new_value = max(metric_type['min'], min(metric_type['max'], current + change))
        
        self.current_values[name] = new_value
        
        # Determine if this is a critical alert
        is_critical = False
        if name == 'error_rate' and new_value > 8:
            is_critical = True
        elif name == 'cpu_usage' and new_value > 90:
            is_critical = True
        elif name == 'request_latency' and new_value > 400:
            is_critical = True
            
        return {
            'name': name,
            'value': round(new_value, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'priority': 'critical' if is_critical else 'normal',
            'tags': {
                'host': f'server-{random.randint(1, 10)}',
                'region': random.choice(['us-east-1', 'us-west-2', 'eu-west-1'])
            }
        }
        
    async def get_history(self, limit: int = 1000) -> List[Dict]:
        """Get historical metrics"""
        return self.history[-limit:]
        
    def get_rate(self) -> float:
        """Get current metrics per second rate"""
        uptime = time.time() - self.start_time
        if uptime > 0:
            return round(self.total_metrics / uptime, 2)
        return 0.0
        
    def get_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        import sys
        return round(sys.getsizeof(self.history) / (1024 * 1024), 2)
        
    def get_uptime(self) -> float:
        """Get uptime in seconds"""
        return round(time.time() - self.start_time, 2)
