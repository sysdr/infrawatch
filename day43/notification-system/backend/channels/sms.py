from channels.base import NotificationChannel
from models.notification import Notification
from config.settings import settings
import logging
from typing import Dict, Any
import re

logger = logging.getLogger(__name__)

class SMSChannel(NotificationChannel):
    """SMS notification channel using Twilio"""
    
    def __init__(self):
        super().__init__()
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_phone
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        # Basic E.164 format validation
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, recipient.replace(' ', '').replace('-', '')))
    
    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            if not self.validate_recipient(notification.recipient):
                raise ValueError(f"Invalid phone format: {notification.recipient}")
            
            formatted_msg = await self.format_message(notification)
            
            # Demo implementation - simulate Twilio API
            logger.info(f"📱 Sending SMS to {notification.recipient}")
            logger.info(f"Message: {formatted_msg['body']}")
            
            # Simulate API response
            return {
                "success": True,
                "message_id": f"sms_{notification.id}_demo",
                "provider": "twilio",
                "cost": 0.0075  # $0.0075 per SMS
            }
            
        except Exception as e:
            logger.error(f"SMS send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "twilio"
            }
    
    async def format_message(self, notification: Notification) -> Dict[str, str]:
        """Format SMS message (160 char limit)"""
        # Truncate for SMS length limits
        title = notification.title[:50]
        priority_prefix = f"[{notification.priority.value.upper()}] "
        
        available_chars = 160 - len(priority_prefix) - len(title) - 3  # 3 for " - "
        message = notification.message[:available_chars]
        if len(notification.message) > available_chars:
            message = message[:-3] + "..."
        
        sms_body = f"{priority_prefix}{title} - {message}"
        
        return {
            "title": title,
            "body": sms_body
        }
