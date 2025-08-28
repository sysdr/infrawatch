import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
import json
import logging

from ..models.metrics import MetricData, AggregatedMetric
from .statistics import StatisticalCalculator

logger = logging.getLogger(__name__)

class TimeWindow:
    """Sliding time window for metric aggregation"""
    
    def __init__(self, window_size: timedelta = timedelta(minutes=5)):
        self.window_size = window_size
        self.data_points = deque()
        self.stats_calculator = StatisticalCalculator()
    
    def add_point(self, metric: MetricData):
        """Add a data point to the window"""
        self.data_points.append((metric.timestamp, metric.value))
        self._cleanup_old_data()
    
    def _cleanup_old_data(self):
        """Remove data points outside the window"""
        cutoff_time = datetime.utcnow() - self.window_size
        while self.data_points and self.data_points[0][0] < cutoff_time:
            self.data_points.popleft()
    
    def get_aggregations(self) -> Dict[str, float]:
        """Calculate aggregations for current window"""
        if not self.data_points:
            return {}
        
        values = [point[1] for point in self.data_points]
        
        return {
            "count": len(values),
            "sum": sum(values),
            "average": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "p50": self.stats_calculator.percentile(values, 50),
            "p95": self.stats_calculator.percentile(values, 95),
            "p99": self.stats_calculator.percentile(values, 99),
            "std_dev": self.stats_calculator.standard_deviation(values),
            "rate_of_change": self.stats_calculator.rate_of_change(values)
        }

class AggregationEngine:
    """Real-time metrics aggregation engine"""
    
    def __init__(self):
        self.windows: Dict[str, TimeWindow] = defaultdict(TimeWindow)
        self.metric_counts = defaultdict(int)
        self.last_aggregation = {}
        self.lock = asyncio.Lock()
    
    async def process_metric(self, metric: MetricData):
        """Process a single metric through the aggregation pipeline"""
        async with self.lock:
            # Create window key based on metric name and tags
            window_key = self._create_window_key(metric)
            
            # Add to appropriate window
            self.windows[window_key].add_point(metric)
            self.metric_counts[window_key] += 1
            
            logger.debug(f"Processed metric: {window_key}, total points: {self.metric_counts[window_key]}")
    
    def _create_window_key(self, metric: MetricData) -> str:
        """Create unique key for metric window"""
        tag_str = "_".join([f"{k}:{v}" for k, v in sorted(metric.tags.items())])
        return f"{metric.name}_{tag_str}"
    
    async def get_current_aggregations(self) -> List[Dict[str, Any]]:
        """Get current aggregations for all windows"""
        async with self.lock:
            aggregations = []
            
            for window_key, window in self.windows.items():
                try:
                    # Parse window key
                    parts = window_key.split('_', 1)
                    metric_name = parts[0]
                    
                    # Get aggregations
                    agg_data = window.get_aggregations()
                    
                    if agg_data:  # Only include windows with data
                        aggregations.append({
                            "metric_name": metric_name,
                            "window_key": window_key,
                            "timestamp": datetime.utcnow().isoformat(),
                            "aggregations": agg_data,
                            "total_processed": self.metric_counts[window_key]
                        })
                        
                except Exception as e:
                    logger.error(f"Error aggregating window {window_key}: {e}")
            
            self.last_aggregation = {
                "timestamp": datetime.utcnow().isoformat(),
                "aggregations": aggregations,
                "total_windows": len(self.windows)
            }
            
            return aggregations
    
    async def get_aggregation_summary(self) -> Dict[str, Any]:
        """Get summary of aggregation engine status"""
        async with self.lock:
            return {
                "active_windows": len(self.windows),
                "total_metrics_processed": sum(self.metric_counts.values()),
                "last_aggregation_time": self.last_aggregation.get("timestamp"),
                "metrics_by_type": dict(self.metric_counts)
            }
    
    async def get_trends(self, metric_name: str, lookback_minutes: int = 30) -> Dict[str, Any]:
        """Calculate trends for a specific metric"""
        # This would typically query historical data
        # For demo, we'll use current window data
        trends = {}
        
        for window_key, window in self.windows.items():
            if window_key.startswith(metric_name):
                data_points = list(window.data_points)
                if len(data_points) >= 2:
                    values = [point[1] for point in data_points]
                    trends[window_key] = {
                        "trend_direction": "up" if values[-1] > values[0] else "down",
                        "change_percent": ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0,
                        "data_points": len(values)
                    }
        
        return trends
