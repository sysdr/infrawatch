from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Alert, Notification, UserPreference, NotificationChannel, NotificationStatus, AlertStatus
from app.core.redis_client import redis_client
from app.services.channel_providers import email_provider, sms_provider, slack_provider
import logging
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class NotificationService:
    
    async def process_alert(self, alert_id: int, db: AsyncSession):
        """Main entry point: alert created, send notifications"""
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            logger.error(f"Alert {alert_id} not found")
            return
        
        # Get recipients based on service and severity
        recipients = await self.get_recipients(alert, db)
        
        # Fan out to channels
        for user_id in recipients:
            await self.send_to_user(alert, user_id, db)
        
        # Update alert status
        alert.status = AlertStatus.NOTIFIED
        await db.commit()
    
    async def get_recipients(self, alert: Alert, db: AsyncSession):
        """Determine who should receive this alert"""
        # In production, this would query subscriptions
        # For demo, return all users
        result = await db.execute(select(UserPreference))
        users = result.scalars().all()
        return [u.user_id for u in users]
    
    async def send_to_user(self, alert: Alert, user_id: str, db: AsyncSession):
        """Send notification to user via their preferred channels"""
        # Load preferences (with cache)
        preferences = await self.get_user_preferences(user_id, db)
        if not preferences:
            logger.warning(f"No preferences for user {user_id}")
            return
        
        # Resolve channels based on severity
        channels = self.resolve_channels(alert.severity.value, preferences.preferences)
        
        for channel in channels:
            await self.send_notification(alert, user_id, channel, preferences, db)
    
    async def get_user_preferences(self, user_id: str, db: AsyncSession):
        """Get preferences with Redis cache"""
        try:
            # Ensure Redis is connected
            if redis_client.redis is None:
                await redis_client.connect()
            
            cached = await redis_client.get_preference_cache(user_id)
            if cached:
                result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
                pref = result.scalar_one_or_none()
                if pref:
                    pref.preferences = cached
                    return pref
        except Exception as e:
            logger.warning(f"Redis cache error (continuing without cache): {e}")
        
        result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        pref = result.scalar_one_or_none()
        
        if pref:
            try:
                if redis_client.redis is None:
                    await redis_client.connect()
                await redis_client.set_preference_cache(user_id, pref.preferences)
            except Exception as e:
                logger.warning(f"Redis cache error (continuing without cache): {e}")
        
        return pref
    
    def resolve_channels(self, severity: str, preferences: dict):
        """Resolve which channels to use based on severity"""
        # Default: all channels for HIGH/CRITICAL
        default_channels = [NotificationChannel.EMAIL]
        
        if severity in ["HIGH", "CRITICAL"]:
            default_channels.extend([NotificationChannel.SMS, NotificationChannel.SLACK])
        
        # Check user overrides
        severity_prefs = preferences.get(severity, {})
        if "channels" in severity_prefs:
            return [NotificationChannel[ch] for ch in severity_prefs["channels"]]
        
        return default_channels
    
    async def send_notification(self, alert: Alert, user_id: str, channel: NotificationChannel, 
                               preferences: UserPreference, db: AsyncSession):
        """Send single notification via channel"""
        # Generate idempotency key
        key_str = f"{alert.id}_{user_id}_{channel.value}_0"
        idempotency_key = hashlib.sha256(key_str.encode()).hexdigest()
        
        # Check if already sent
        result = await db.execute(
            select(Notification).where(Notification.idempotency_key == idempotency_key)
        )
        if result.scalar_one_or_none():
            logger.info(f"Notification already sent: {idempotency_key}")
            return
        
        # Check circuit breaker
        try:
            if redis_client.redis is None:
                await redis_client.connect()
            if await redis_client.circuit_breaker_is_open(channel.value):
                logger.warning(f"Circuit breaker open for {channel.value}")
                notification = Notification(
                    alert_id=alert.id,
                    user_id=user_id,
                    channel=channel,
                    status=NotificationStatus.FAILED,
                    idempotency_key=idempotency_key,
                    message=alert.message,
                    failed_reason="Circuit breaker open"
                )
                db.add(notification)
                await db.commit()
                return
        except Exception as e:
            logger.warning(f"Redis circuit breaker check error (continuing): {e}")
        
        # Create notification record
        notification = Notification(
            alert_id=alert.id,
            user_id=user_id,
            channel=channel,
            idempotency_key=idempotency_key,
            message=alert.message
        )
        db.add(notification)
        await db.commit()
        
        # Send via channel
        try:
            if channel == NotificationChannel.EMAIL:
                await email_provider.send(preferences.email, alert.message, alert.alert_metadata)
            elif channel == NotificationChannel.SMS:
                if preferences.phone:
                    await sms_provider.send(preferences.phone, alert.message)
            elif channel == NotificationChannel.SLACK:
                if preferences.slack_id:
                    await slack_provider.send(preferences.slack_id, alert.message, alert.alert_metadata)
            
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Notification sent: {idempotency_key}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            notification.status = NotificationStatus.FAILED
            notification.failed_reason = str(e)
            notification.retry_count += 1
            await db.commit()
            
            # Open circuit breaker if multiple failures
            if notification.retry_count >= 3:
                try:
                    if redis_client.redis is None:
                        await redis_client.connect()
                    await redis_client.open_circuit_breaker(channel.value, 30)
                except Exception as e:
                    logger.warning(f"Redis circuit breaker error (continuing): {e}")

notification_service = NotificationService()
