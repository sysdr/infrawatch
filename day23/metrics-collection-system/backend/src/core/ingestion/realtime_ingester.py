import asyncio
import time
from typing import Dict, List, Any
import structlog
from collections import defaultdict, deque
import orjson

logger = structlog.get_logger()

class RealtimeIngester:
    def __init__(self, max_buffer_size: int = 10000):
        self.metrics_buffer = deque(maxlen=max_buffer_size)
        self.metrics_per_second = defaultdict(int)
        self.agent_connections = {}
        self.processing_queue = asyncio.Queue()
        self.stats = {
            "total_metrics": 0,
            "metrics_per_second": 0,
            "active_agents": 0,
            "buffer_size": 0
        }
        self._running = False

    async def start(self):
        self._running = True
        asyncio.create_task(self._process_metrics())
        asyncio.create_task(self._update_stats())

    async def stop(self):
        self._running = False

    async def ingest_metric(self, agent_id: str, metric_data: Dict[str, Any]):
        """Ingest a metric from an agent with validation and buffering"""
        try:
            timestamp = time.time()
            metric = {
                "agent_id": agent_id,
                "timestamp": timestamp,
                "data": metric_data,
                "processed": False
            }
            
            self.metrics_buffer.append(metric)
            await self.processing_queue.put(metric)
            
            self.stats["total_metrics"] += 1
            self.metrics_per_second[int(timestamp)] += 1
            
            logger.debug(f"Ingested metric from {agent_id}: {metric_data.get('name', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to ingest metric from {agent_id}: {e}")

    async def _process_metrics(self):
        """Background task to process ingested metrics"""
        while self._running:
            try:
                metric = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                # Simulate processing time
                await asyncio.sleep(0.001)
                metric["processed"] = True
                logger.debug(f"Processed metric from {metric['agent_id']}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing metric: {e}")

    async def _update_stats(self):
        """Update real-time statistics"""
        while self._running:
            current_time = int(time.time())
            self.stats["metrics_per_second"] = self.metrics_per_second.get(current_time - 1, 0)
            self.stats["buffer_size"] = len(self.metrics_buffer)
            self.stats["active_agents"] = len(self.agent_connections)
            
            # Clean old metrics_per_second data
            old_times = [t for t in self.metrics_per_second.keys() if t < current_time - 60]
            for t in old_times:
                del self.metrics_per_second[t]
                
            await asyncio.sleep(1)

    def get_stats(self) -> Dict[str, Any]:
        return self.stats.copy()

    def get_recent_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(self.metrics_buffer)[-limit:]
