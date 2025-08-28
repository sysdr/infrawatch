import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

from ..models.metrics import MetricData, AggregatedMetric

logger = logging.getLogger(__name__)

class TimeSeriesStorage:
    """Time-series data storage implementation"""
    
    def __init__(self):
        # In-memory storage for demo (would be replaced with InfluxDB, TimescaleDB, etc.)
        self.raw_metrics = []
        self.aggregated_metrics = []
        self.max_raw_points = 10000  # Limit for demo
        self.max_aggregated_points = 5000
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize storage connection"""
        logger.info("Initializing time-series storage...")
        # In a real implementation, this would connect to the database
        await asyncio.sleep(0.1)  # Simulate connection time
        logger.info("Time-series storage initialized")
    
    async def close(self):
        """Close storage connection"""
        logger.info("Closing time-series storage connection")
        # Cleanup would happen here
    
    async def store_metric(self, metric: MetricData) -> bool:
        """Store a raw metric data point"""
        async with self.lock:
            try:
                # Convert to dict for storage
                metric_dict = {
                    "name": metric.name,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "tags": metric.tags
                }
                
                self.raw_metrics.append(metric_dict)
                
                # Maintain size limit
                if len(self.raw_metrics) > self.max_raw_points:
                    self.raw_metrics = self.raw_metrics[-self.max_raw_points:]
                
                logger.debug(f"Stored metric: {metric.name} = {metric.value}")
                return True
                
            except Exception as e:
                logger.error(f"Error storing metric: {e}")
                return False
    
    async def store_aggregated_metric(self, metric: AggregatedMetric) -> bool:
        """Store an aggregated metric"""
        async with self.lock:
            try:
                # Convert to dict for storage
                metric_dict = {
                    "name": metric.name,
                    "aggregations": metric.aggregations,
                    "timestamp": metric.timestamp.isoformat(),
                    "resolution": metric.resolution,
                    "tags": metric.tags,
                    "sample_count": metric.sample_count
                }
                
                self.aggregated_metrics.append(metric_dict)
                
                # Maintain size limit
                if len(self.aggregated_metrics) > self.max_aggregated_points:
                    self.aggregated_metrics = self.aggregated_metrics[-self.max_aggregated_points:]
                
                logger.debug(f"Stored aggregated metric: {metric.name} ({metric.resolution})")
                return True
                
            except Exception as e:
                logger.error(f"Error storing aggregated metric: {e}")
                return False
    
    async def query_metrics(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime,
        tags: Dict[str, str] = None,
        resolution: str = None
    ) -> List[Dict[str, Any]]:
        """Query metrics within a time range"""
        async with self.lock:
            try:
                # Choose appropriate storage based on resolution
                if resolution and resolution != "raw":
                    source_data = self.aggregated_metrics
                else:
                    source_data = self.raw_metrics
                
                results = []
                
                for metric_dict in source_data:
                    # Check metric name
                    if metric_dict["name"] != metric_name:
                        continue
                    
                    # Check time range
                    metric_time = datetime.fromisoformat(metric_dict["timestamp"])
                    if not (start_time <= metric_time <= end_time):
                        continue
                    
                    # Check tags if specified
                    if tags:
                        metric_tags = metric_dict.get("tags", {})
                        if not all(metric_tags.get(k) == v for k, v in tags.items()):
                            continue
                    
                    # Check resolution if specified
                    if resolution and resolution != "raw":
                        if metric_dict.get("resolution") != resolution:
                            continue
                    
                    results.append(metric_dict)
                
                # Sort by timestamp
                results.sort(key=lambda x: x["timestamp"])
                
                logger.debug(f"Query returned {len(results)} metrics for {metric_name}")
                return results
                
            except Exception as e:
                logger.error(f"Error querying metrics: {e}")
                return []
    
    async def get_metric_names(self) -> List[str]:
        """Get list of all metric names"""
        async with self.lock:
            names = set()
            
            for metric_dict in self.raw_metrics:
                names.add(metric_dict["name"])
            
            for metric_dict in self.aggregated_metrics:
                names.add(metric_dict["name"])
            
            return sorted(list(names))
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        async with self.lock:
            return {
                "raw_metrics_count": len(self.raw_metrics),
                "aggregated_metrics_count": len(self.aggregated_metrics),
                "max_raw_points": self.max_raw_points,
                "max_aggregated_points": self.max_aggregated_points,
                "storage_utilization": {
                    "raw": (len(self.raw_metrics) / self.max_raw_points) * 100,
                    "aggregated": (len(self.aggregated_metrics) / self.max_aggregated_points) * 100
                }
            }
    
    async def cleanup_old_data(self, retention_days: int = 7):
        """Clean up old data based on retention policy"""
        async with self.lock:
            try:
                cutoff_time = datetime.utcnow() - timedelta(days=retention_days)
                cutoff_str = cutoff_time.isoformat()
                
                # Clean raw metrics
                original_raw_count = len(self.raw_metrics)
                self.raw_metrics = [
                    m for m in self.raw_metrics 
                    if m["timestamp"] > cutoff_str
                ]
                
                # Clean aggregated metrics
                original_agg_count = len(self.aggregated_metrics)
                self.aggregated_metrics = [
                    m for m in self.aggregated_metrics 
                    if m["timestamp"] > cutoff_str
                ]
                
                cleaned_raw = original_raw_count - len(self.raw_metrics)
                cleaned_agg = original_agg_count - len(self.aggregated_metrics)
                
                logger.info(f"Cleaned up {cleaned_raw} raw metrics and {cleaned_agg} aggregated metrics")
                
                return {
                    "cleaned_raw": cleaned_raw,
                    "cleaned_aggregated": cleaned_agg,
                    "remaining_raw": len(self.raw_metrics),
                    "remaining_aggregated": len(self.aggregated_metrics)
                }
                
            except Exception as e:
                logger.error(f"Error cleaning up old data: {e}")
                return {"error": str(e)}
