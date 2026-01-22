from typing import Dict
from datetime import datetime
import random

class HealthMonitor:
    """Monitors service health metrics"""
    
    def calculate_health_score(self, metrics: Dict) -> int:
        """Calculate composite health score (0-100)"""
        availability = metrics.get('availability', 1.0)
        latency_p95 = metrics.get('latency_p95', 50)
        error_rate = metrics.get('error_rate', 0.0)
        cpu_util = metrics.get('cpu_utilization', 50)
        
        # Weighted scoring
        availability_score = availability * 40
        
        # Latency score (inverse)
        if latency_p95 < 100:
            latency_score = 30
        elif latency_p95 < 500:
            latency_score = 20
        else:
            latency_score = 10
        
        # Error rate score
        if error_rate < 0.01:
            error_score = 20
        elif error_rate < 0.05:
            error_score = 10
        else:
            error_score = 5
        
        # CPU saturation score
        if cpu_util < 80:
            saturation_score = 10
        elif cpu_util < 90:
            saturation_score = 5
        else:
            saturation_score = 0
        
        total_score = int(availability_score + latency_score + error_score + saturation_score)
        return min(max(total_score, 0), 100)
    
    def get_health_status(self, score: int) -> str:
        """Determine health status from score"""
        if score >= 90:
            return "healthy"
        elif score >= 50:
            return "degraded"
        else:
            return "unhealthy"
    
    async def collect_health_metrics(self, resource: Dict) -> Dict:
        """Collect health metrics for a resource"""
        # Simulate realistic metrics
        return {
            'availability': 0.999,
            'latency_p95': random.uniform(20, 150),
            'error_rate': random.uniform(0, 0.02),
            'cpu_utilization': random.uniform(20, 85),
            'memory_utilization': random.uniform(30, 75),
            'timestamp': datetime.utcnow().isoformat()
        }
