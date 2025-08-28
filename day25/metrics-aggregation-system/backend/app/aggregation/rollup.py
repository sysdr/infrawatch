import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict

from ..models.metrics import AggregatedMetric
from ..storage.timeseries import TimeSeriesStorage
from .statistics import StatisticalCalculator

logger = logging.getLogger(__name__)

class RollupManager:
    """Manages rollup operations for historical data aggregation"""
    
    def __init__(self):
        self.storage = TimeSeriesStorage()
        self.stats_calculator = StatisticalCalculator()
        self.last_rollup = {}
        
        # Define rollup configurations
        self.rollup_configs = {
            "1m": {"source_resolution": "1s", "retention": timedelta(hours=6)},
            "5m": {"source_resolution": "1m", "retention": timedelta(days=1)},
            "1h": {"source_resolution": "5m", "retention": timedelta(days=7)},
            "1d": {"source_resolution": "1h", "retention": timedelta(days=365)}
        }
    
    async def perform_rollups(self):
        """Perform all configured rollup operations"""
        try:
            logger.info("Starting rollup operations...")
            
            # Perform rollups in order (fine to coarse granularity)
            for resolution, config in self.rollup_configs.items():
                await self._perform_single_rollup(resolution, config)
            
            # Update last rollup timestamp
            self.last_rollup = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            logger.info("Rollup operations completed successfully")
            
        except Exception as e:
            logger.error(f"Error performing rollups: {e}")
            self.last_rollup = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    async def _perform_single_rollup(self, target_resolution: str, config: Dict[str, Any]):
        """Perform rollup for a specific resolution"""
        try:
            # Calculate time range for rollup
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)  # Process last hour
            
            # Get raw data to aggregate
            raw_metrics = await self._get_metrics_for_rollup(start_time, end_time, config["source_resolution"])
            
            if not raw_metrics:
                logger.debug(f"No metrics found for rollup {target_resolution}")
                return
            
            # Group metrics by name and tags for aggregation
            grouped_metrics = self._group_metrics_for_rollup(raw_metrics, target_resolution)
            
            # Calculate aggregations
            aggregated_metrics = []
            for group_key, metrics in grouped_metrics.items():
                aggregated = await self._calculate_rollup_aggregation(metrics, target_resolution)
                if aggregated:
                    aggregated_metrics.append(aggregated)
            
            # Store aggregated metrics
            if aggregated_metrics:
                await self._store_rollup_results(aggregated_metrics, target_resolution)
                logger.info(f"Completed rollup for {target_resolution}: {len(aggregated_metrics)} aggregations")
            
        except Exception as e:
            logger.error(f"Error in rollup for {target_resolution}: {e}")
    
    async def _get_metrics_for_rollup(self, start_time: datetime, end_time: datetime, source_resolution: str) -> List[Dict[str, Any]]:
        """Retrieve metrics for rollup processing"""
        # This would query the actual time-series database
        # For demo purposes, we'll simulate some data
        
        sample_metrics = []
        current_time = start_time
        
        while current_time < end_time:
            for metric_name in ["cpu_usage", "memory_usage", "request_count"]:
                for server in ["server-1", "server-2"]:
                    sample_metrics.append({
                        "name": metric_name,
                        "value": 50.0 + (current_time.minute % 30),  # Simulate varying data
                        "timestamp": current_time,
                        "tags": {"server": server, "environment": "demo"}
                    })
            
            current_time += timedelta(minutes=1)
        
        return sample_metrics
    
    def _group_metrics_for_rollup(self, metrics: List[Dict[str, Any]], target_resolution: str) -> Dict[str, List[Dict[str, Any]]]:
        """Group metrics by name and tags for aggregation"""
        grouped = defaultdict(list)
        
        for metric in metrics:
            # Create grouping key
            tag_str = "_".join([f"{k}:{v}" for k, v in sorted(metric["tags"].items())])
            group_key = f"{metric['name']}_{tag_str}"
            grouped[group_key].append(metric)
        
        return dict(grouped)
    
    async def _calculate_rollup_aggregation(self, metrics: List[Dict[str, Any]], target_resolution: str) -> Optional[AggregatedMetric]:
        """Calculate aggregated values for a group of metrics"""
        if not metrics:
            return None
        
        try:
            values = [m["value"] for m in metrics]
            first_metric = metrics[0]
            
            # Calculate aggregations using statistical calculator
            aggregations = {
                "count": len(values),
                "sum": sum(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p50": self.stats_calculator.percentile(values, 50),
                "p95": self.stats_calculator.percentile(values, 95),
                "p99": self.stats_calculator.percentile(values, 99),
                "std_dev": self.stats_calculator.standard_deviation(values),
                "rate_of_change": self.stats_calculator.rate_of_change(values)
            }
            
            return AggregatedMetric(
                name=first_metric["name"],
                aggregations=aggregations,
                timestamp=datetime.utcnow(),
                resolution=target_resolution,
                tags=first_metric["tags"],
                sample_count=len(values)
            )
            
        except Exception as e:
            logger.error(f"Error calculating rollup aggregation: {e}")
            return None
    
    async def _store_rollup_results(self, aggregated_metrics: List[AggregatedMetric], resolution: str):
        """Store rollup results to time-series database"""
        try:
            # In a real implementation, this would write to the time-series database
            logger.info(f"Storing {len(aggregated_metrics)} rollup results for resolution {resolution}")
            
            # For demo, we'll just log the aggregations
            for metric in aggregated_metrics:
                logger.debug(f"Rollup {resolution}: {metric.name} = {metric.aggregations.get('average', 0):.2f}")
            
        except Exception as e:
            logger.error(f"Error storing rollup results: {e}")
    
    async def get_rollup_status(self) -> Dict[str, Any]:
        """Get current rollup status"""
        return {
            "last_rollup": self.last_rollup,
            "configured_resolutions": list(self.rollup_configs.keys()),
            "next_rollup": (datetime.utcnow() + timedelta(minutes=1)).isoformat()
        }
    
    async def cleanup_old_data(self):
        """Clean up data based on retention policies"""
        try:
            for resolution, config in self.rollup_configs.items():
                cutoff_time = datetime.utcnow() - config["retention"]
                await self._cleanup_resolution_data(resolution, cutoff_time)
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def _cleanup_resolution_data(self, resolution: str, cutoff_time: datetime):
        """Clean up data for a specific resolution"""
        # This would delete old data from the time-series database
        logger.info(f"Cleaned up {resolution} data older than {cutoff_time}")
