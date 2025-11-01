"""
Mock delivery services for testing notification channels
"""

import asyncio
import random
import time
from typing import Dict, Optional
import structlog

logger = structlog.get_logger()

class DeliveryMockManager:
    """
    Manages mock delivery services for different notification channels
    """
    
    def __init__(self):
        self.mock_configs = {
            "email": {"success_rate": 0.95, "latency_ms": (100, 300)},
            "sms": {"success_rate": 0.90, "latency_ms": (200, 800)},
            "push": {"success_rate": 0.88, "latency_ms": (50, 150)},
            "webhook": {"success_rate": 0.92, "latency_ms": (150, 500)}
        }
        self.delivery_logs = []

    async def initialize(self):
        """Initialize mock delivery services"""
        logger.info("Initializing mock delivery services")
        
        # Simulate initialization delay
        await asyncio.sleep(0.1)
        
        logger.info("Mock delivery services initialized", 
                   channels=list(self.mock_configs.keys()))

    async def configure_mocks(self, config: Dict):
        """Configure mock service behavior"""
        for channel, settings in config.items():
            if channel in self.mock_configs:
                self.mock_configs[channel].update(settings)
                logger.info(f"Updated mock config for {channel}", 
                          config=self.mock_configs[channel])

    async def deliver_notification(self, channel: str, user_id: str, content: str) -> bool:
        """
        Simulate notification delivery with configurable success/failure rates
        """
        config = self.mock_configs.get(channel, {"success_rate": 0.5, "latency_ms": (100, 500)})
        
        # Simulate network latency
        min_latency, max_latency = config["latency_ms"]
        latency = random.uniform(min_latency, max_latency)
        await asyncio.sleep(latency / 1000.0)  # Convert to seconds
        
        # Determine success based on configured rate
        success = random.random() < config["success_rate"]
        
        # Log delivery attempt
        log_entry = {
            "timestamp": time.time(),
            "channel": channel,
            "user_id": user_id,
            "success": success,
            "latency_ms": latency,
            "content_length": len(content)
        }
        self.delivery_logs.append(log_entry)
        
        # Keep only recent logs
        if len(self.delivery_logs) > 10000:
            self.delivery_logs = self.delivery_logs[-5000:]
        
        if success:
            logger.info(f"Mock delivery successful", 
                       channel=channel, user_id=user_id, latency_ms=latency)
        else:
            logger.warning(f"Mock delivery failed", 
                          channel=channel, user_id=user_id, latency_ms=latency)
        
        return success

    def get_delivery_stats(self, channel: Optional[str] = None) -> Dict:
        """Get delivery statistics"""
        logs = self.delivery_logs
        
        if channel:
            logs = [log for log in logs if log["channel"] == channel]
        
        if not logs:
            return {"total": 0, "success_rate": 0, "avg_latency_ms": 0}
        
        total = len(logs)
        successful = sum(1 for log in logs if log["success"])
        avg_latency = sum(log["latency_ms"] for log in logs) / total
        
        return {
            "total": total,
            "successful": successful,
            "success_rate": successful / total,
            "avg_latency_ms": avg_latency,
            "recent_logs": logs[-10:]  # Last 10 entries
        }

    def simulate_service_degradation(self, channel: str, duration_seconds: int = 60):
        """Simulate service degradation for testing"""
        original_config = self.mock_configs[channel].copy()
        
        # Reduce success rate temporarily
        self.mock_configs[channel]["success_rate"] = 0.3
        self.mock_configs[channel]["latency_ms"] = (500, 2000)
        
        logger.warning(f"Simulating degradation for {channel}", duration=duration_seconds)
        
        # Schedule restoration
        async def restore_service():
            await asyncio.sleep(duration_seconds)
            self.mock_configs[channel] = original_config
            logger.info(f"Service restored for {channel}")
        
        asyncio.create_task(restore_service())

class EmailMockService:
    """Mock email delivery service"""
    
    @staticmethod
    async def send_email(to: str, subject: str, body: str) -> Dict:
        # Simulate email provider API call
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        success = random.random() < 0.95  # 95% success rate
        
        return {
            "success": success,
            "message_id": f"email_{int(time.time())}_{random.randint(1000, 9999)}",
            "provider": "mock_sendgrid",
            "latency_ms": random.uniform(100, 300)
        }

class SMSMockService:
    """Mock SMS delivery service"""
    
    @staticmethod
    async def send_sms(to: str, message: str) -> Dict:
        # Simulate SMS provider API call
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        success = random.random() < 0.90  # 90% success rate
        
        return {
            "success": success,
            "message_id": f"sms_{int(time.time())}_{random.randint(1000, 9999)}",
            "provider": "mock_twilio",
            "latency_ms": random.uniform(200, 800)
        }

class PushMockService:
    """Mock push notification service"""
    
    @staticmethod
    async def send_push(device_token: str, title: str, body: str) -> Dict:
        # Simulate push provider API call
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        success = random.random() < 0.88  # 88% success rate
        
        return {
            "success": success,
            "message_id": f"push_{int(time.time())}_{random.randint(1000, 9999)}",
            "provider": "mock_fcm",
            "latency_ms": random.uniform(50, 150)
        }
