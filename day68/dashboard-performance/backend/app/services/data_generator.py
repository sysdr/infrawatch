import random
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

class DataGenerator:
    def __init__(self):
        self.metric_names = [
            "cpu_usage", "memory_usage", "disk_io", "network_rx", "network_tx",
            "api_latency", "error_rate", "request_rate", "active_users", "db_connections"
        ]
        self.current_values = {name: random.uniform(20, 80) for name in self.metric_names}
    
    def generate_time_series(self, points: int = 100, metric: str = "cpu_usage") -> List[Dict]:
        """Generate realistic time-series data with trends and noise"""
        now = datetime.now()
        data = []
        
        # Use current value as starting point
        base_value = self.current_values.get(metric, 50.0)
        
        for i in range(points):
            # Add trend and noise
            trend = np.sin(i / 10) * 10  # Sinusoidal trend
            noise = random.gauss(0, 5)  # Random noise
            value = max(0, min(100, base_value + trend + noise))
            
            data.append({
                "timestamp": (now - timedelta(minutes=points-i)).isoformat(),
                "value": round(value, 2),
                "metric": metric
            })
        
        return data
    
    def generate_metric_updates(self, count: int = 50) -> List[Dict]:
        """Generate random metric updates"""
        updates = []
        
        for _ in range(count):
            metric = random.choice(self.metric_names)
            
            # Gradual change from current value
            current = self.current_values[metric]
            change = random.gauss(0, 3)
            new_value = max(0, min(100, current + change))
            self.current_values[metric] = new_value
            
            updates.append({
                "metric_id": metric,
                "value": round(new_value, 2),
                "timestamp": datetime.now().isoformat()
            })
        
        return updates
    
    def generate_chart_data(self, chart_type: str, resolution: int = 100) -> Dict:
        """Generate optimized chart data based on type"""
        if chart_type == "line":
            return {
                "type": "line",
                "data": self.generate_time_series(resolution),
                "downsampled": resolution < 1920
            }
        elif chart_type == "bar":
            categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            return {
                "type": "bar",
                "data": [{"category": cat, "value": random.uniform(100, 1000)} for cat in categories]
            }
        elif chart_type == "scatter":
            return {
                "type": "scatter",
                "data": [{"x": random.uniform(0, 100), "y": random.uniform(0, 100)} for _ in range(min(resolution, 500))]
            }
        return {}
    
    def downsample_lttb(self, data: List[Dict], threshold: int) -> List[Dict]:
        """Largest-Triangle-Three-Buckets downsampling algorithm"""
        if len(data) <= threshold:
            return data
        
        # Always keep first and last points
        sampled = [data[0]]
        
        # Calculate bucket size
        bucket_size = (len(data) - 2) / (threshold - 2)
        
        a = 0  # Initially set to first point
        
        for i in range(threshold - 2):
            # Calculate average point in next bucket
            avg_x = 0
            avg_y = 0
            avg_range_start = int((i + 1) * bucket_size) + 1
            avg_range_end = int((i + 2) * bucket_size) + 1
            avg_range_end = min(avg_range_end, len(data))
            
            for j in range(avg_range_start, avg_range_end):
                avg_x += j
                avg_y += data[j]["value"]
            
            avg_x /= (avg_range_end - avg_range_start)
            avg_y /= (avg_range_end - avg_range_start)
            
            # Find point with largest triangle area
            range_start = int(i * bucket_size) + 1
            range_end = int((i + 1) * bucket_size) + 1
            
            max_area = -1
            max_area_point = None
            
            for j in range(range_start, range_end):
                # Calculate triangle area
                area = abs((data[a]["value"] - avg_y) * (j - avg_x) - 
                          (data[a]["value"] - data[j]["value"]) * (a - avg_x)) / 2
                
                if area > max_area:
                    max_area = area
                    max_area_point = data[j]
                    a = j
            
            if max_area_point:
                sampled.append(max_area_point)
        
        sampled.append(data[-1])  # Always keep last point
        return sampled

data_generator = DataGenerator()
