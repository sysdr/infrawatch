from channels.base import NotificationChannel
from models.notification import Notification
import logging
from typing import Dict, Any
import json
import httpx
import asyncio

logger = logging.getLogger(__name__)

class WebhookChannel(NotificationChannel):
    """Webhook notification channel"""
    
    def __init__(self):
        super().__init__()
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate webhook URL format"""
        return recipient.startswith(('http://', 'https://'))
    
    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            if not self.validate_recipient(notification.recipient):
                raise ValueError(f"Invalid webhook URL: {notification.recipient}")
            
            formatted_msg = await self.format_message(notification)
            payload = {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority.value,
                "timestamp": notification.created_at.isoformat(),
                "channel": "webhook",
                "metadata": json.loads(notification.metadata) if notification.metadata else {}
            }
            
            # Demo implementation - simulate webhook call
            logger.info(f"🔗 Sending webhook to {notification.recipient}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            # In production, use:
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         notification.recipient,
            #         json=payload,
            #         timeout=30.0
            #     )
            
            # Simulate successful response
            return {
                "success": True,
                "message_id": f"webhook_{notification.id}_demo",
                "provider": "webhook",
                "status_code": 200,
                "cost": 0.0
            }
            
        except Exception as e:
            logger.error(f"Webhook send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "webhook"
            }
    
    async def format_message(self, notification: Notification) -> Dict[str, str]:
        """Format webhook payload"""
        return {
            "title": notification.title,
            "body": notification.message
        }
