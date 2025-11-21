import asyncio
import logging
from datetime import datetime
from ..utils.db_pool import db_pool
from ..utils.redis_queue import redis_queue
from ..models.notification import NotificationCreate, Notification
from .connection_manager import manager

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.processing = False
        self.latency_samples = []
        
    async def create_notification(self, notification: NotificationCreate) -> Notification:
        """Create notification and queue for delivery"""
        start_time = datetime.now()
        
        async with db_pool.get_connection() as conn:
            # Insert into database
            row = await conn.fetchrow(
                """
                INSERT INTO notifications (user_id, message, priority, notification_type, created_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, user_id, message, priority, notification_type, created_at, delivered
                """,
                notification.user_id,
                notification.message,
                notification.priority,
                notification.notification_type,
                datetime.now()
            )
            
            notif = Notification(
                id=row['id'],
                user_id=row['user_id'],
                message=row['message'],
                priority=row['priority'],
                notification_type=row['notification_type'],
                created_at=row['created_at'],
                delivered=row['delivered']
            )
            
            # Queue for delivery
            await redis_queue.enqueue(
                "notifications",
                notif.model_dump(mode='json'),
                priority=notification.priority
            )
            
            # Track latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.latency_samples.append(latency_ms)
            if len(self.latency_samples) > 1000:
                self.latency_samples.pop(0)
            
            logger.debug(f"Created notification {notif.id} for {notif.user_id}")
            
            return notif
    
    async def start_worker(self):
        """Start background worker to process notification queue"""
        self.processing = True
        logger.info("Notification worker started")
        
        while self.processing:
            try:
                # Dequeue notification
                message = await redis_queue.dequeue("notifications", timeout=1)
                
                if message:
                    # Add to connection manager buffer
                    user_id = message['user_id']
                    await manager.add_to_buffer(user_id, message)
                    
                    # Mark as delivered in database
                    async with db_pool.get_connection() as conn:
                        await conn.execute(
                            """
                            UPDATE notifications 
                            SET delivered = true, delivered_at = $1
                            WHERE id = $2
                            """,
                            datetime.now(),
                            message['id']
                        )
                
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)
    
    async def stop_worker(self):
        """Stop background worker"""
        self.processing = False
        logger.info("Notification worker stopped")
    
    def get_average_latency(self) -> float:
        """Calculate average latency from recent samples"""
        if not self.latency_samples:
            return 0.0
        return sum(self.latency_samples) / len(self.latency_samples)

notification_service = NotificationService()
