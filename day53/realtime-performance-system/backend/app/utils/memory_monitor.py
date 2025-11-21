import os
import psutil
import asyncio
import logging
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)

class MemoryMonitor:
    def __init__(self, max_samples: int = 60):
        self.process = psutil.Process()
        self.memory_history = deque(maxlen=max_samples)
        self.monitoring = False
        
    async def start_monitoring(self):
        """Start background memory monitoring"""
        self.monitoring = True
        asyncio.create_task(self._monitor_loop())
        logger.info("Memory monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    async def _monitor_loop(self):
        """Monitor memory usage every second"""
        while self.monitoring:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            self.memory_history.append({
                'timestamp': datetime.now(),
                'memory_mb': memory_mb
            })
            
            if memory_mb > int(os.getenv("MEMORY_LIMIT_MB", 2000)):
                logger.warning(f"High memory usage: {memory_mb:.2f}MB")
            
            await asyncio.sleep(1)
    
    def get_current_memory(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_history(self) -> list:
        """Get memory usage history"""
        return list(self.memory_history)

memory_monitor = MemoryMonitor()
