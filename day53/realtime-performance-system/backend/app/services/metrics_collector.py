import asyncio
import logging
from datetime import datetime
from collections import deque
from ..utils.memory_monitor import memory_monitor
from ..utils.redis_queue import redis_queue
from .connection_manager import manager
from .notification_service import notification_service

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics_history = deque(maxlen=60)  # Last 60 seconds
        self.collecting = False
        self.last_message_count = 0
        
    async def start_collection(self):
        """Start collecting metrics every second"""
        self.collecting = True
        asyncio.create_task(self._collect_loop())
        logger.info("Metrics collection started")
    
    async def stop_collection(self):
        """Stop collecting metrics"""
        self.collecting = False
    
    async def _collect_loop(self):
        """Collect metrics every second"""
        while self.collecting:
            try:
                # Gather metrics
                current_messages = manager.metrics['total_messages']
                messages_per_second = current_messages - self.last_message_count
                self.last_message_count = current_messages
                
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'active_connections': manager.get_connection_count(),
                    'memory_usage_mb': memory_monitor.get_current_memory(),
                    'messages_per_second': messages_per_second,
                    'average_latency_ms': notification_service.get_average_latency(),
                    'queue_depth': await redis_queue.get_queue_depth("notifications"),
                    'total_messages': current_messages,
                    'compression_ratio': manager.get_metrics()['compression_ratio']
                }
                
                self.metrics_history.append(metrics)
                
                # Broadcast to dashboard via Redis Pub/Sub
                await redis_queue.publish("metrics", metrics)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
            
            await asyncio.sleep(1)
    
    def get_current_metrics(self) -> dict:
        """Get most recent metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}
    
    def get_metrics_history(self) -> list:
        """Get metrics history"""
        return list(self.metrics_history)

metrics_collector = MetricsCollector()
