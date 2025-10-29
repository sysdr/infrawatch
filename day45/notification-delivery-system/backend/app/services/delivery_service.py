import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import random
from enum import Enum

logger = logging.getLogger(__name__)

class DeliveryStatus(Enum):
    SUCCESS = "success"
    FAILED_TEMPORARY = "failed_temporary"
    FAILED_PERMANENT = "failed_permanent"
    RATE_LIMITED = "rate_limited"

@dataclass
class DeliveryResult:
    status: DeliveryStatus
    message: str
    delivery_time_ms: float
    response_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None

class DeliveryService:
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.delivery_stats = {
            "total_sent": 0,
            "successful": 0,
            "failed_temporary": 0,
            "failed_permanent": 0,
            "rate_limited": 0,
            "avg_delivery_time": 0.0
        }
        self.running = False
        
    async def start_delivery_worker(self):
        """Start the delivery worker"""
        self.running = True
        logger.info("🚀 Starting delivery worker...")
        
        while self.running:
            try:
                # This would integrate with the queue manager
                # For demo, we'll simulate periodic deliveries
                await self._simulate_delivery_work()
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Delivery worker error: {e}")
                await asyncio.sleep(5)
    
    async def _simulate_delivery_work(self):
        """Simulate delivery work for demo"""
        # Simulate processing some notifications
        for i in range(random.randint(1, 5)):
            notification_data = {
                "id": f"demo_notif_{datetime.now().timestamp()}_{i}",
                "channel": random.choice(["email", "sms", "push"]),
                "recipient": f"user_{random.randint(1, 100)}@example.com",
                "content": f"Demo notification {i}",
                "priority": random.choice(["low", "normal", "high", "urgent"])
            }
            
            result = await self.deliver_notification(notification_data)
            
            # Send real-time update via WebSocket
            await self.websocket_manager.broadcast({
                "type": "delivery_update",
                "notification": notification_data,
                "result": {
                    "status": result.status.value,
                    "message": result.message,
                    "delivery_time_ms": result.delivery_time_ms
                },
                "timestamp": datetime.now().isoformat()
            })
    
    async def deliver_notification(self, notification_data: Dict[str, Any]) -> DeliveryResult:
        """Deliver a single notification"""
        start_time = datetime.now()
        
        try:
            channel = notification_data.get("channel", "email")
            
            # Simulate delivery based on channel
            if channel == "email":
                result = await self._deliver_email(notification_data)
            elif channel == "sms":
                result = await self._deliver_sms(notification_data)
            elif channel == "push":
                result = await self._deliver_push(notification_data)
            else:
                result = DeliveryResult(
                    status=DeliveryStatus.FAILED_PERMANENT,
                    message=f"Unsupported channel: {channel}",
                    delivery_time_ms=0.0,
                    error_code="UNSUPPORTED_CHANNEL"
                )
            
            # Update stats
            self.delivery_stats["total_sent"] += 1
            if result.status == DeliveryStatus.SUCCESS:
                self.delivery_stats["successful"] += 1
            elif result.status == DeliveryStatus.FAILED_TEMPORARY:
                self.delivery_stats["failed_temporary"] += 1
            elif result.status == DeliveryStatus.FAILED_PERMANENT:
                self.delivery_stats["failed_permanent"] += 1
            elif result.status == DeliveryStatus.RATE_LIMITED:
                self.delivery_stats["rate_limited"] += 1
            
            # Update average delivery time
            total_time = self.delivery_stats["avg_delivery_time"] * (self.delivery_stats["total_sent"] - 1)
            self.delivery_stats["avg_delivery_time"] = (total_time + result.delivery_time_ms) / self.delivery_stats["total_sent"]
            
            return result
            
        except Exception as e:
            delivery_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Delivery failed: {e}")
            return DeliveryResult(
                status=DeliveryStatus.FAILED_TEMPORARY,
                message=f"Delivery error: {str(e)}",
                delivery_time_ms=delivery_time,
                error_code="DELIVERY_ERROR"
            )
    
    async def _deliver_email(self, notification_data: Dict[str, Any]) -> DeliveryResult:
        """Simulate email delivery"""
        start_time = datetime.now()
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            delivery_time = (datetime.now() - start_time).total_seconds() * 1000
            return DeliveryResult(
                status=DeliveryStatus.FAILED_TEMPORARY,
                message="SMTP server timeout",
                delivery_time_ms=delivery_time,
                error_code="SMTP_TIMEOUT"
            )
        
        delivery_time = (datetime.now() - start_time).total_seconds() * 1000
        return DeliveryResult(
            status=DeliveryStatus.SUCCESS,
            message="Email delivered successfully",
            delivery_time_ms=delivery_time,
            response_data={"message_id": f"email_{datetime.now().timestamp()}"}
        )
    
    async def _deliver_sms(self, notification_data: Dict[str, Any]) -> DeliveryResult:
        """Simulate SMS delivery"""
        start_time = datetime.now()
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.05, 0.3))
        
        # Simulate rate limiting
        if random.random() < 0.05:  # 5% rate limit
            delivery_time = (datetime.now() - start_time).total_seconds() * 1000
            return DeliveryResult(
                status=DeliveryStatus.RATE_LIMITED,
                message="SMS rate limit exceeded",
                delivery_time_ms=delivery_time,
                error_code="RATE_LIMIT_EXCEEDED"
            )
        
        delivery_time = (datetime.now() - start_time).total_seconds() * 1000
        return DeliveryResult(
            status=DeliveryStatus.SUCCESS,
            message="SMS delivered successfully",
            delivery_time_ms=delivery_time,
            response_data={"sms_id": f"sms_{datetime.now().timestamp()}"}
        )
    
    async def _deliver_push(self, notification_data: Dict[str, Any]) -> DeliveryResult:
        """Simulate push notification delivery"""
        start_time = datetime.now()
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.02, 0.2))
        
        # Simulate device not found (permanent failure)
        if random.random() < 0.03:  # 3% permanent failure
            delivery_time = (datetime.now() - start_time).total_seconds() * 1000
            return DeliveryResult(
                status=DeliveryStatus.FAILED_PERMANENT,
                message="Device token invalid",
                delivery_time_ms=delivery_time,
                error_code="INVALID_DEVICE_TOKEN"
            )
        
        delivery_time = (datetime.now() - start_time).total_seconds() * 1000
        return DeliveryResult(
            status=DeliveryStatus.SUCCESS,
            message="Push notification delivered successfully",
            delivery_time_ms=delivery_time,
            response_data={"push_id": f"push_{datetime.now().timestamp()}"}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        return self.delivery_stats.copy()
    
    def is_healthy(self) -> bool:
        """Health check"""
        return self.running
    
    def stop(self):
        """Stop delivery service"""
        self.running = False
        logger.info("🛑 Delivery service stopped")
