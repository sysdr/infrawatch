import asyncio
import psutil
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class MetricCollector:
    def __init__(self, stream_manager):
        self.stream_manager = stream_manager
        self.running = False
        self.total_collected = 0
        self.last_metrics: Dict = {}
        self.significant_threshold = 5.0  # 5% change is significant
        
    async def start_collection(self):
        """Start collecting metrics"""
        self.running = True
        logger.info("Metric collector started")
        
        while self.running:
            try:
                metrics = await self.collect_metrics()
                self.total_collected += 1
                
                # Check if change is significant
                if self._is_significant_change(metrics):
                    # Immediate broadcast for significant changes
                    await self.stream_manager.broadcast(
                        'metrics_update',
                        metrics,
                        priority='normal'
                    )
                else:
                    # Queue for batched delivery
                    await self.stream_manager.broadcast(
                        'metrics_update',
                        metrics,
                        priority='low'
                    )
                    
                self.last_metrics = metrics
                await asyncio.sleep(1)  # Collect every second
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(1)
                
    async def collect_metrics(self) -> Dict:
        """Collect system metrics"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        return {
            'timestamp': time.time(),
            'cpu': {
                'percent': round(cpu_percent, 2),
                'count': psutil.cpu_count()
            },
            'memory': {
                'percent': round(memory.percent, 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2)
            },
            'disk': {
                'percent': round(disk.percent, 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2)
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        }
        
    def _is_significant_change(self, current: Dict) -> bool:
        """Check if metrics changed significantly"""
        if not self.last_metrics:
            return True
            
        # Check CPU change
        cpu_change = abs(current.get('cpu', {}).get('percent', 0) - 
                        self.last_metrics.get('cpu', {}).get('percent', 0))
        if cpu_change > self.significant_threshold:
            return True
            
        # Check memory change
        mem_change = abs(current.get('memory', {}).get('percent', 0) - 
                        self.last_metrics.get('memory', {}).get('percent', 0))
        if mem_change > self.significant_threshold:
            return True
            
        return False
        
    async def stop(self):
        self.running = False
        logger.info("Metric collector stopped")
