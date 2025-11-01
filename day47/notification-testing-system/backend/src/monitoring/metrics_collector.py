"""
Metrics collection and real-time monitoring
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, List
import structlog

logger = structlog.get_logger()

class MetricsCollector:
    """
    Collects and manages real-time system metrics
    """
    
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=3600))  # 1 hour at 1s intervals
        self.current_metrics = {}
        self.running = False
        self.collection_interval = 1.0  # seconds

    async def start(self):
        """Start metrics collection"""
        self.running = True
        asyncio.create_task(self._collection_loop())
        logger.info("Metrics collector started")

    async def stop(self):
        """Stop metrics collection"""
        self.running = False
        logger.info("Metrics collector stopped")

    async def _collection_loop(self):
        """Main metrics collection loop"""
        while self.running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)

    async def _collect_system_metrics(self):
        """Collect current system metrics"""
        timestamp = time.time()
        
        # System-level metrics
        metrics = {
            "timestamp": timestamp,
            "system": await self._get_system_metrics(),
            "notifications": await self._get_notification_metrics(),
            "performance": await self._get_performance_metrics(),
            "reliability": await self._get_reliability_metrics()
        }
        
        # Store in history
        self.current_metrics = metrics
        for category, values in metrics.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    metric_key = f"{category}.{key}"
                    self.metrics_history[metric_key].append({
                        "timestamp": timestamp,
                        "value": value
                    })

    async def _get_system_metrics(self) -> Dict:
        """Get system-level metrics"""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections()),
                "process_count": len(psutil.pids())
            }
        except ImportError:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "network_connections": 0,
                "process_count": 0
            }

    async def _get_notification_metrics(self) -> Dict:
        """Get notification-specific metrics"""
        return {
            "total_sent": self._get_counter_value("notifications_sent"),
            "total_failed": self._get_counter_value("notifications_failed"),
            "email_sent": self._get_counter_value("email_sent"),
            "sms_sent": self._get_counter_value("sms_sent"),
            "push_sent": self._get_counter_value("push_sent"),
            "webhook_sent": self._get_counter_value("webhook_sent")
        }

    async def _get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        return {
            "avg_response_time": self._get_gauge_value("avg_response_time"),
            "p95_response_time": self._get_gauge_value("p95_response_time"),
            "requests_per_second": self._get_gauge_value("requests_per_second"),
            "active_connections": self._get_gauge_value("active_connections"),
            "queue_depth": self._get_gauge_value("queue_depth")
        }

    async def _get_reliability_metrics(self) -> Dict:
        """Get reliability metrics"""
        return {
            "uptime_percent": 99.5,  # Would be calculated from actual uptime
            "circuit_breakers_open": self._get_gauge_value("circuit_breakers_open"),
            "retry_rate": self._get_gauge_value("retry_rate"),
            "error_rate": self._get_gauge_value("error_rate"),
            "availability_score": self._get_gauge_value("availability_score", 0.99)
        }

    def _get_counter_value(self, metric_name: str) -> int:
        """Get counter value (would integrate with actual metrics system)"""
        # In real implementation, this would query Prometheus, StatsD, etc.
        return len([m for m in self.metrics_history.get(metric_name, []) 
                   if time.time() - m["timestamp"] < 60])

    def _get_gauge_value(self, metric_name: str, default: float = 0.0) -> float:
        """Get gauge value (would integrate with actual metrics system)"""
        history = self.metrics_history.get(metric_name, [])
        if history:
            return history[-1]["value"]
        return default

    async def record_notification_attempt(self, channel: str, success: bool):
        """Record a notification attempt"""
        timestamp = time.time()
        
        # Record general metrics
        self.metrics_history["notifications_sent"].append({
            "timestamp": timestamp,
            "value": 1
        })
        
        if not success:
            self.metrics_history["notifications_failed"].append({
                "timestamp": timestamp,
                "value": 1
            })
        
        # Record channel-specific metrics
        self.metrics_history[f"{channel}_sent"].append({
            "timestamp": timestamp,
            "value": 1
        })

    async def get_current_metrics(self) -> Dict:
        """Get current real-time metrics"""
        if not self.current_metrics:
            await self._collect_system_metrics()
        
        return self.current_metrics

    async def get_historical_metrics(self, hours: int = 1) -> Dict:
        """Get historical metrics for specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        
        historical_data = {}
        
        for metric_name, history in self.metrics_history.items():
            # Filter to requested time period
            recent_data = [
                point for point in history 
                if point["timestamp"] >= cutoff_time
            ]
            
            if recent_data:
                historical_data[metric_name] = {
                    "data_points": recent_data,
                    "average": sum(p["value"] for p in recent_data) / len(recent_data),
                    "min": min(p["value"] for p in recent_data),
                    "max": max(p["value"] for p in recent_data),
                    "latest": recent_data[-1]["value"]
                }
        
        return {
            "time_range_hours": hours,
            "metrics": historical_data,
            "summary": {
                "total_data_points": sum(len(data["data_points"]) for data in historical_data.values()),
                "metrics_count": len(historical_data)
            }
        }

    def get_timestamp(self) -> float:
        """Get current timestamp"""
        return time.time()

    def get_metrics_summary(self) -> Dict:
        """Get summary of all collected metrics"""
        return {
            "active_metrics": len(self.metrics_history),
            "total_data_points": sum(len(history) for history in self.metrics_history.values()),
            "collection_running": self.running,
            "latest_collection": self.current_metrics.get("timestamp", 0)
        }
