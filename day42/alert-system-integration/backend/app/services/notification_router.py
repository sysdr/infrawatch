import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from ..models import Alert, Notification, NotificationStatus

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False
    
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.is_open = False
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("Circuit breaker opened due to repeated failures")
    
    def can_attempt(self) -> bool:
        """Check if we can attempt a call"""
        if not self.is_open:
            return True
            
        if self.last_failure_time:
            if (datetime.now() - self.last_failure_time).total_seconds() > self.timeout:
                logger.info("Circuit breaker half-open, attempting recovery")
                self.is_open = False
                self.failure_count = 0
                return True
        
        return False

class NotificationRouter:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.notifications: Dict[str, Notification] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.dead_letter_queue: List[Notification] = []
        
    async def route_notification(self, alert: Alert):
        """Route alert to appropriate notification channels"""
        channel = "default"  # Could be determined by alert severity/labels
        
        notification = Notification(
            id=f"notif_{alert.id}_{int(datetime.now().timestamp())}",
            alert_id=alert.id,
            channel=channel,
            status=NotificationStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.notifications[notification.id] = notification
        await self._send_notification(notification, alert)
    
    async def _send_notification(self, notification: Notification, alert: Alert):
        """Send notification with retry logic and circuit breaker"""
        channel = notification.channel
        
        if channel not in self.circuit_breakers:
            self.circuit_breakers[channel] = CircuitBreaker()
        
        circuit_breaker = self.circuit_breakers[channel]
        
        if not circuit_breaker.can_attempt():
            logger.warning(f"Circuit breaker open for channel {channel}, skipping notification")
            notification.status = NotificationStatus.FAILED
            notification.error_message = "Circuit breaker open"
            self.dead_letter_queue.append(notification)
            return
        
        for attempt in range(notification.max_attempts):
            try:
                notification.attempts = attempt + 1
                notification.status = NotificationStatus.RETRYING if attempt > 0 else NotificationStatus.PENDING
                
                # Simulate notification sending (replace with actual implementation)
                await self._do_send(notification, alert)
                
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now()
                circuit_breaker.record_success()
                logger.info(f"Notification {notification.id} sent successfully")
                return
                
            except Exception as e:
                logger.error(f"Notification attempt {attempt + 1} failed: {e}")
                circuit_breaker.record_failure()
                
                if attempt < notification.max_attempts - 1:
                    # Exponential backoff
                    delay = (2 ** attempt) * 5
                    await asyncio.sleep(delay)
                else:
                    notification.status = NotificationStatus.FAILED
                    notification.error_message = str(e)
                    self.dead_letter_queue.append(notification)
    
    async def _do_send(self, notification: Notification, alert: Alert):
        """Actual notification sending logic"""
        # Simulate sending with occasional failures for testing
        await asyncio.sleep(0.1)
        logger.info(f"Sending notification for alert: {alert.rule_name} - {alert.message}")
        # In production, this would call actual notification services
    
    async def send_resolution_notification(self, alert: Alert):
        """Send notification when alert is resolved"""
        logger.info(f"Alert resolved: {alert.rule_name}")
        # Similar to route_notification but with resolution message
