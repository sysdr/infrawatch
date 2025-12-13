import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

class ChartService:
    def generate_multi_series(
        self, 
        metrics: List[str], 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict[str, Any]:
        """Generate multi-series time-series data"""
        time_range = pd.date_range(start=start_time, end=end_time, freq='5min')
        
        series_data = []
        for metric in metrics:
            # Simulate realistic metric patterns
            base_value = np.random.uniform(50, 100)
            noise = np.random.normal(0, 10, len(time_range))
            trend = np.linspace(0, 20, len(time_range))
            values = base_value + noise + trend
            
            # Add some spikes for realism
            spike_indices = np.random.choice(len(values), size=5, replace=False)
            values[spike_indices] *= 1.5
            
            series_data.append({
                "name": metric,
                "data": [
                    {"timestamp": ts.isoformat(), "value": float(v)}
                    for ts, v in zip(time_range, values)
                ]
            })
        
        return {
            "series": series_data,
            "metadata": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "interval": "5min",
                "count": len(time_range)
            }
        }
    
    def generate_stacked_data(
        self, 
        categories: List[str], 
        series: List[str]
    ) -> Dict[str, Any]:
        """Generate stacked bar/area data"""
        data_points = []
        
        for category in categories:
            point = {"category": category}
            for series_name in series:
                # Generate values that sum to meaningful totals
                point[series_name] = float(np.random.uniform(10, 100))
            data_points.append(point)
        
        # Calculate cumulative values for stacking
        stacked_points = []
        for point in data_points:
            stacked = {"category": point["category"]}
            cumulative = 0
            for series_name in series:
                value = point[series_name]
                stacked[series_name] = value
                stacked[f"{series_name}_stacked"] = cumulative + value
                cumulative += value
            stacked_points.append(stacked)
        
        return {
            "data": stacked_points,
            "series": series,
            "categories": categories
        }
    
    def generate_scatter_data(
        self, 
        x_metric: str, 
        y_metric: str, 
        samples: int
    ) -> Dict[str, Any]:
        """Generate scatter plot data with correlation"""
        # Create correlated data
        correlation = np.random.uniform(0.3, 0.9)
        
        x_values = np.random.uniform(0, 100, samples)
        y_values = correlation * x_values + np.random.normal(0, 10, samples)
        
        # Add some outliers
        outlier_count = int(samples * 0.05)
        outlier_indices = np.random.choice(samples, outlier_count, replace=False)
        y_values[outlier_indices] += np.random.uniform(-50, 50, outlier_count)
        
        points = [
            {
                "x": float(x),
                "y": float(y),
                "label": f"Point {i}",
                "outlier": i in outlier_indices
            }
            for i, (x, y) in enumerate(zip(x_values, y_values))
        ]
        
        # Calculate correlation coefficient
        correlation_coef = np.corrcoef(x_values, y_values)[0, 1]
        
        return {
            "data": points,
            "x_metric": x_metric,
            "y_metric": y_metric,
            "correlation": float(correlation_coef),
            "outliers": len(outlier_indices)
        }
    
    def generate_heatmap_data(
        self, 
        metric: str, 
        days: int
    ) -> Dict[str, Any]:
        """Generate heatmap data bucketed by hour and day"""
        cells = []
        
        day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        
        for day in range(days):
            for hour in range(24):
                # Simulate patterns: higher during business hours
                base_value = 50
                if 9 <= hour <= 17:  # Business hours
                    base_value = 150
                
                value = base_value + np.random.uniform(-20, 20)
                
                cells.append({
                    "day": day_labels[day % 7],
                    "hour": hour,
                    "value": float(value),
                    "timestamp": (datetime.now() - timedelta(days=days-day, hours=24-hour)).isoformat()
                })
        
        return {
            "data": cells,
            "metric": metric,
            "days": days,
            "value_range": {
                "min": min(c["value"] for c in cells),
                "max": max(c["value"] for c in cells)
            }
        }
    
    def generate_latency_distribution(self) -> Dict[str, Any]:
        """Generate latency distribution for box plot"""
        percentiles = [50, 75, 90, 95, 99]
        services = ["api", "database", "cache", "external"]
        
        distributions = []
        for service in services:
            base_latency = np.random.uniform(10, 50)
            values = np.random.exponential(base_latency, 1000)
            
            dist = {
                "service": service,
                "min": float(np.min(values)),
                "q1": float(np.percentile(values, 25)),
                "median": float(np.percentile(values, 50)),
                "q3": float(np.percentile(values, 75)),
                "max": float(np.max(values)),
                "outliers": [float(v) for v in values if v > np.percentile(values, 99)][:10]
            }
            
            for p in percentiles:
                dist[f"p{p}"] = float(np.percentile(values, p))
            
            distributions.append(dist)
        
        return {
            "distributions": distributions,
            "percentiles": percentiles
        }
    
    def generate_status_timeline(self, hours: int) -> Dict[str, Any]:
        """Generate service status timeline"""
        statuses = ["healthy", "degraded", "down"]
        status_colors = {"healthy": "#10b981", "degraded": "#f59e0b", "down": "#ef4444"}
        
        services = ["api-gateway", "auth-service", "payment-service", "notification-service"]
        
        timeline = []
        current_time = datetime.now()
        
        for service in services:
            events = []
            time = current_time - timedelta(hours=hours)
            
            while time < current_time:
                duration = timedelta(minutes=np.random.randint(15, 120))
                status = np.random.choice(statuses, p=[0.85, 0.10, 0.05])
                
                events.append({
                    "start": time.isoformat(),
                    "end": (time + duration).isoformat(),
                    "status": status,
                    "color": status_colors[status]
                })
                
                time += duration
            
            timeline.append({
                "service": service,
                "events": events
            })
        
        return {
            "timeline": timeline,
            "statuses": statuses,
            "hours": hours
        }
