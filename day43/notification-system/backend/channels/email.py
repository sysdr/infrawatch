from channels.base import NotificationChannel
from models.notification import Notification
from config.settings import settings
import json
import logging
from typing import Dict, Any
import re

logger = logging.getLogger(__name__)

class EmailChannel(NotificationChannel):
    """Email notification channel using SendGrid"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.from_email
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, recipient))
    
    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send email notification"""
        try:
            if not self.validate_recipient(notification.recipient):
                raise ValueError(f"Invalid email format: {notification.recipient}")
            
            # Simulate SendGrid API call
            # In production, use sendgrid.SendGridAPIClient
            
            formatted_msg = await self.format_message(notification)
            
            # Demo implementation - simulate API call
            logger.info(f"📧 Sending email to {notification.recipient}")
            logger.info(f"Subject: {formatted_msg['title']}")
            logger.info(f"Body: {formatted_msg['body'][:100]}...")
            
            # Simulate API response
            return {
                "success": True,
                "message_id": f"email_{notification.id}_demo",
                "provider": "sendgrid",
                "cost": 0.001  # $0.001 per email
            }
            
        except Exception as e:
            logger.error(f"Email send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "sendgrid"
            }
    
    async def format_message(self, notification: Notification) -> Dict[str, str]:
        """Format email with HTML template"""
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #333; margin-top: 0;">{notification.title}</h2>
                <div style="background: white; padding: 20px; border-radius: 4px; margin: 16px 0;">
                    <p style="color: #555; line-height: 1.6;">{notification.message}</p>
                </div>
                <div style="color: #666; font-size: 12px; margin-top: 20px;">
                    <p>Priority: {notification.priority.value.upper()}</p>
                    <p>Sent: {notification.created_at}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return {
            "title": f"[{notification.priority.value.upper()}] {notification.title}",
            "body": notification.message,
            "html_body": html_body
        }
