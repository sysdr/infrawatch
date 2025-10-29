import asyncio
import redis.asyncio as redis
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import heapq

logger = logging.getLogger(__name__)

@dataclass
class QueuedNotification:
    id: str
    priority: int
    scheduled_at: datetime
    notification_data: Dict[str, Any]
    
    def __lt__(self, other):
        # Higher priority first, then earlier scheduled time
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.scheduled_at < other.scheduled_at

class QueueManager:
    def __init__(self):
        self.redis_client = None
        self.priority_queue = []
        self.processing = False
        self.stats = {
            "queued": 0,
            "processed": 0,
            "failed": 0,
            "processing_rate": 0.0
        }
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory queue.")
            self.redis_client = None
    
    async def enqueue_notification(self, notification_data: Dict[str, Any]) -> str:
        """Add notification to queue"""
        notification_id = f"notif_{datetime.now().timestamp()}_{id(notification_data)}"
        
        queued_notif = QueuedNotification(
            id=notification_id,
            priority=self._get_priority_score(notification_data.get("priority", "normal")),
            scheduled_at=datetime.fromisoformat(notification_data.get("scheduled_at", datetime.now().isoformat())),
            notification_data=notification_data
        )
        
        # Add to priority queue
        heapq.heappush(self.priority_queue, queued_notif)
        self.stats["queued"] += 1
        
        # Also add to Redis if available
        if self.redis_client:
            try:
                await self.redis_client.lpush("notification_queue", json.dumps({
                    "id": notification_id,
                    "data": notification_data,
                    "queued_at": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Failed to add to Redis queue: {e}")
        
        logger.info(f"📥 Queued notification {notification_id}")
        return notification_id
    
    def _get_priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score"""
        priority_map = {
            "low": 1,
            "normal": 5,
            "high": 8,
            "urgent": 10
        }
        return priority_map.get(priority.lower(), 5)
    
    async def dequeue_batch(self, batch_size: int = 10) -> List[QueuedNotification]:
        """Get batch of notifications ready for processing"""
        ready_notifications = []
        current_time = datetime.now()
        
        # Process from priority queue
        temp_queue = []
        
        while self.priority_queue and len(ready_notifications) < batch_size:
            notification = heapq.heappop(self.priority_queue)
            
            if notification.scheduled_at <= current_time:
                ready_notifications.append(notification)
            else:
                # Put back notifications not ready yet
                temp_queue.append(notification)
        
        # Put back non-ready notifications
        for notif in temp_queue:
            heapq.heappush(self.priority_queue, notif)
        
        return ready_notifications
    
    async def start_processing(self):
        """Start the queue processing loop"""
        await self.connect()
        self.processing = True
        logger.info("🔄 Starting queue processing...")
        
        while self.processing:
            try:
                start_time = datetime.now()
                
                # Get batch of notifications
                notifications = await self.dequeue_batch(batch_size=10)
                
                if notifications:
                    # Process batch (this would typically send to delivery service)
                    for notification in notifications:
                        await self._process_notification(notification)
                        self.stats["processed"] += 1
                    
                    # Calculate processing rate
                    processing_time = (datetime.now() - start_time).total_seconds()
                    self.stats["processing_rate"] = len(notifications) / max(processing_time, 0.001)
                    
                    logger.info(f"📤 Processed batch of {len(notifications)} notifications")
                else:
                    # No notifications ready, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                self.stats["failed"] += 1
                await asyncio.sleep(5)
    
    async def _process_notification(self, notification: QueuedNotification):
        """Process a single notification (placeholder for delivery service integration)"""
        # This would typically send the notification to the delivery service
        logger.info(f"Processing notification {notification.id}")
        
        # Simulate processing time
        await asyncio.sleep(0.1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            **self.stats,
            "queue_size": len(self.priority_queue),
            "processing": self.processing
        }
    
    def is_healthy(self) -> bool:
        """Health check"""
        return self.processing and len(self.priority_queue) < 10000
    
    async def stop(self):
        """Stop queue processing"""
        self.processing = False
        if self.redis_client:
            await self.redis_client.close()
        logger.info("🛑 Queue processing stopped")
