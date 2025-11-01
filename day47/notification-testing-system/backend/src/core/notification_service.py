"""
Core notification service with reliability patterns
"""

import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import structlog

from .circuit_breaker import CircuitBreaker
from mocks.delivery_mocks import DeliveryMockManager

logger = structlog.get_logger()

@dataclass
class NotificationRequest:
    user_id: str
    channel: str
    content: str
    priority: str = "normal"
    metadata: Optional[Dict] = None

@dataclass
class DeliveryResult:
    success: bool
    channel: str
    latency_ms: float
    error: Optional[str] = None
    attempt_count: int = 1

class NotificationService:
    def __init__(self):
        self.circuit_breakers = {}
        self.delivery_mocks = DeliveryMockManager()
        self.retry_config = {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 30.0
        }
        
    async def initialize(self):
        """Initialize the notification service"""
        await self.delivery_mocks.initialize()
        
        # Initialize circuit breakers for each channel
        channels = ["email", "sms", "push", "webhook"]
        for channel in channels:
            self.circuit_breakers[channel] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30.0,
                expected_exception=Exception
            )

    async def send_notification(self, notification_data: Dict) -> Dict:
        """Send notification with reliability patterns"""
        start_time = time.time()
        
        try:
            request = NotificationRequest(
                user_id=notification_data["user_id"],
                channel=notification_data["channel"],
                content=notification_data["content"],
                priority=notification_data.get("priority", "normal"),
                metadata=notification_data.get("metadata", {})
            )
            
            # Check circuit breaker
            circuit_breaker = self.circuit_breakers.get(request.channel)
            if circuit_breaker and circuit_breaker.is_open():
                return {
                    "success": False,
                    "error": f"Circuit breaker open for {request.channel}",
                    "latency_ms": (time.time() - start_time) * 1000
                }
            
            # Attempt delivery with retries
            result = await self._attempt_delivery_with_retries(request)
            
            # Update circuit breaker
            if circuit_breaker:
                if result.success:
                    circuit_breaker.record_success()
                else:
                    circuit_breaker.record_failure()
            
            return {
                "success": result.success,
                "channel": result.channel,
                "latency_ms": result.latency_ms,
                "error": result.error,
                "attempts": result.attempt_count
            }
            
        except Exception as e:
            logger.error("Notification send failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "latency_ms": (time.time() - start_time) * 1000
            }

    async def _attempt_delivery_with_retries(self, request: NotificationRequest) -> DeliveryResult:
        """Attempt delivery with exponential backoff retries"""
        last_error = None
        
        for attempt in range(self.retry_config["max_retries"] + 1):
            try:
                start_time = time.time()
                
                # Use mock delivery service
                success = await self.delivery_mocks.deliver_notification(
                    request.channel,
                    request.user_id,
                    request.content
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                if success:
                    return DeliveryResult(
                        success=True,
                        channel=request.channel,
                        latency_ms=latency_ms,
                        attempt_count=attempt + 1
                    )
                else:
                    last_error = "Mock delivery failed"
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    "Delivery attempt failed",
                    attempt=attempt + 1,
                    channel=request.channel,
                    error=str(e)
                )
            
            # Calculate delay for next retry
            if attempt < self.retry_config["max_retries"]:
                delay = min(
                    self.retry_config["base_delay"] * (2 ** attempt),
                    self.retry_config["max_delay"]
                )
                await asyncio.sleep(delay)
        
        return DeliveryResult(
            success=False,
            channel=request.channel,
            latency_ms=0,
            error=last_error,
            attempt_count=self.retry_config["max_retries"] + 1
        )

    async def get_channel_health(self) -> Dict[str, Dict]:
        """Get health status for all channels"""
        health_status = {}
        
        for channel, circuit_breaker in self.circuit_breakers.items():
            health_status[channel] = {
                "status": "healthy" if not circuit_breaker.is_open() else "circuit_open",
                "failure_count": circuit_breaker.failure_count,
                "last_failure": circuit_breaker.last_failure_time
            }
            
        return health_status
