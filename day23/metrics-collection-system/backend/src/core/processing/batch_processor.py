import asyncio
import time
from typing import Dict, List, Any
import structlog
from collections import defaultdict

logger = structlog.get_logger()

class BatchProcessor:
    def __init__(self, batch_size: int = 100, batch_timeout: int = 30):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.batches = defaultdict(list)
        self.last_flush = defaultdict(float)
        self._running = False

    async def start(self):
        self._running = True
        asyncio.create_task(self._process_batches())

    async def stop(self):
        self._running = False

    async def add_to_batch(self, metric_type: str, metric_data: Dict[str, Any]):
        """Add metric to appropriate batch for processing"""
        try:
            self.batches[metric_type].append({
                "timestamp": time.time(),
                "data": metric_data
            })
            
            # Check if batch is ready for processing
            if len(self.batches[metric_type]) >= self.batch_size:
                await self._flush_batch(metric_type)
                
        except Exception as e:
            logger.error(f"Failed to add metric to batch {metric_type}: {e}")

    async def _process_batches(self):
        """Background task to process batches based on timeout"""
        while self._running:
            try:
                current_time = time.time()
                for metric_type, batch in self.batches.items():
                    if (batch and 
                        current_time - self.last_flush.get(metric_type, 0) > self.batch_timeout):
                        await self._flush_batch(metric_type)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")

    async def _flush_batch(self, metric_type: str):
        """Flush and process a complete batch"""
        try:
            batch = self.batches[metric_type].copy()
            self.batches[metric_type].clear()
            self.last_flush[metric_type] = time.time()
            
            if batch:
                # Simulate batch processing (aggregation, compression, etc.)
                await self._process_batch_data(metric_type, batch)
                logger.info(f"Processed batch of {len(batch)} {metric_type} metrics")
                
        except Exception as e:
            logger.error(f"Failed to flush batch {metric_type}: {e}")

    async def _process_batch_data(self, metric_type: str, batch: List[Dict[str, Any]]):
        """Process batch data - aggregation, compression, storage preparation"""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Example aggregations
        if metric_type == "cpu":
            avg_cpu = sum(item["data"].get("value", 0) for item in batch) / len(batch)
            logger.debug(f"CPU batch average: {avg_cpu:.2f}%")
        elif metric_type == "memory":
            avg_memory = sum(item["data"].get("value", 0) for item in batch) / len(batch)
            logger.debug(f"Memory batch average: {avg_memory:.2f}%")

    def get_batch_stats(self) -> Dict[str, Any]:
        return {
            "active_batches": len(self.batches),
            "batch_sizes": {k: len(v) for k, v in self.batches.items()},
            "total_queued": sum(len(v) for v in self.batches.values())
        }
