from typing import Dict, List
from datetime import datetime
import statistics

class MetricsCollector:
    """Collect and aggregate system metrics"""
    
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.latencies: Dict[str, List[float]] = {}
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric"""
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += value
    
    def record_latency(self, operation: str, latency_ms: float):
        """Record operation latency"""
        if operation not in self.latencies:
            self.latencies[operation] = []
        self.latencies[operation].append(latency_ms)
        
        # Keep only last 1000 measurements
        if len(self.latencies[operation]) > 1000:
            self.latencies[operation] = self.latencies[operation][-1000:]
    
    def get_average_latency(self, operation: str) -> float:
        """Get average latency for operation"""
        if operation not in self.latencies or not self.latencies[operation]:
            return 0.0
        return statistics.mean(self.latencies[operation])
    
    def get_percentile(self, operation: str, percentile: int) -> float:
        """Get latency percentile"""
        if operation not in self.latencies or not self.latencies[operation]:
            return 0.0
        
        sorted_latencies = sorted(self.latencies[operation])
        index = int(len(sorted_latencies) * (percentile / 100))
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]
    
    def get_summary(self) -> Dict:
        """Get metrics summary"""
        summary = {
            "counters": self.counters.copy(),
            "latencies": {}
        }
        
        for operation in self.latencies:
            if self.latencies[operation]:
                summary["latencies"][operation] = {
                    "avg": round(self.get_average_latency(operation), 2),
                    "p50": round(self.get_percentile(operation, 50), 2),
                    "p95": round(self.get_percentile(operation, 95), 2),
                    "p99": round(self.get_percentile(operation, 99), 2)
                }
        
        return summary
