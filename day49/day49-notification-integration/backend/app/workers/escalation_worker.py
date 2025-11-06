from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Alert, EscalationPolicy, AlertStatus, AlertSeverity
from app.services.notification_service import notification_service
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class EscalationWorker:
    
    async def run(self, db: AsyncSession):
        """Check for alerts needing escalation"""
        logger.info("Escalation worker running...")
        
        # Find unacknowledged alerts
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        result = await db.execute(
            select(Alert).where(
                Alert.status.in_([AlertStatus.NEW, AlertStatus.NOTIFIED]),
                Alert.created_at < cutoff_time
            )
        )
        alerts = result.scalars().all()
        
        for alert in alerts:
            await self.escalate_alert(alert, db)
    
    async def escalate_alert(self, alert: Alert, db: AsyncSession):
        """Escalate to next tier"""
        logger.info(f"Escalating alert {alert.id}")
        
        # Get escalation policy
        result = await db.execute(
            select(EscalationPolicy).where(
                EscalationPolicy.service_name == alert.service_name,
                EscalationPolicy.severity == alert.severity
            )
        )
        policy = result.scalar_one_or_none()
        
        if not policy:
            logger.warning(f"No escalation policy for {alert.service_name}/{alert.severity}")
            return
        
        # Get next level
        next_level = alert.escalation_level + 1
        config = policy.policy_config
        
        if next_level >= len(config):
            logger.warning(f"Alert {alert.id} reached max escalation level")
            return
        
        level_config = config[next_level]
        users = level_config.get("users", [])
        
        # Send to next tier
        for user_id in users:
            await notification_service.send_to_user(alert, user_id, db)
        
        alert.escalation_level = next_level
        alert.status = AlertStatus.ESCALATED
        await db.commit()
        
        logger.info(f"Alert {alert.id} escalated to level {next_level}")

escalation_worker = EscalationWorker()
