import logging
import asyncio

logger = logging.getLogger(__name__)

class EmailProvider:
    async def send(self, to: str, message: str, metadata: dict):
        """Send email notification"""
        logger.info(f"Sending email to {to}: {message}")
        # Simulate API call
        await asyncio.sleep(0.1)
        logger.info(f"Email sent to {to}")

class SMSProvider:
    async def send(self, to: str, message: str):
        """Send SMS notification"""
        logger.info(f"Sending SMS to {to}: {message}")
        await asyncio.sleep(0.1)
        logger.info(f"SMS sent to {to}")

class SlackProvider:
    async def send(self, user_id: str, message: str, metadata: dict):
        """Send Slack notification"""
        logger.info(f"Sending Slack to {user_id}: {message}")
        await asyncio.sleep(0.1)
        logger.info(f"Slack sent to {user_id}")

email_provider = EmailProvider()
sms_provider = SMSProvider()
slack_provider = SlackProvider()
