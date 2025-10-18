from channels.base import NotificationChannel
from models.notification import Notification
from config.settings import settings
import logging
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)

class PushChannel(NotificationChannel):
    """Push notification channel using Firebase"""
    
    def __init__(self):
        super().__init__()
        self.credentials_path = settings.firebase_credentials_path
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate Firebase token format"""
        # Basic FCM token validation (tokens are typically 152+ chars)
        return len(recipient) > 150 and ':' in recipient
    
    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send push notification"""
        try:
            # For demo, accept any non-empty string as valid token
            if not notification.recipient or len(notification.recipient) < 10:
                raise ValueError(f"Invalid push token: {notification.recipient}")
            
            formatted_msg = await self.format_message(notification)
            
            # Demo implementation - simulate Firebase FCM
            logger.info(f"📲 Sending push notification to device")
            logger.info(f"Title: {formatted_msg['title']}")
            logger.info(f"Body: {formatted_msg['body']}")
            
            # Simulate API response
            return {
                "success": True,
                "message_id": f"push_{notification.id}_demo",
                "provider": "firebase",
                "cost": 0.0  # Firebase has generous free tier
            }
            
        except Exception as e:
            logger.error(f"Push send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "firebase"
            }
    
    async def format_message(self, notification: Notification) -> Dict[str, str]:
        """Format push notification"""
        
        priority_icons = {
            "low": "ℹ️",
            "medium": "⚠️", 
            "high": "🚨",
            "critical": "🔥"
        }
        
        icon = priority_icons.get(notification.priority.value, "📱")
        
        return {
            "title": f"{icon} {notification.title}",
            "body": notification.message[:100] + ("..." if len(notification.message) > 100 else ""),
            "icon": icon,
            "badge": "1",
            "sound": "default" if notification.priority.value in ["high", "critical"] else None
        }
