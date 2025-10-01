import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.alert_rule import AlertInstance, AlertState, AlertSeverity
from .rule_evaluator import EvaluationResult

logger = logging.getLogger(__name__)

class AlertGenerator:
    def __init__(self):
        self.alert_queue = asyncio.Queue()
    
    async def generate_alert(self, result: EvaluationResult, db: AsyncSession) -> AlertInstance:
        """Generate alert instance from evaluation result."""
        fingerprint = self._create_fingerprint(result)
        
        # Check if alert instance already exists
        stmt = select(AlertInstance).where(AlertInstance.fingerprint == fingerprint)
        existing = await db.execute(stmt)
        alert_instance = existing.scalar_one_or_none()
        
        if alert_instance:
            # Update existing alert
            alert_instance.state = AlertState.FIRING
            alert_instance.value = result.value
            alert_instance.updated_at = datetime.utcnow()
        else:
            # Create new alert instance
            alert_instance = AlertInstance(
                rule_id=result.rule_id,
                fingerprint=fingerprint,
                state=AlertState.FIRING,
                value=result.value,
                labels=result.labels,
                annotations={'message': result.message},
                starts_at=datetime.utcnow()
            )
            db.add(alert_instance)
        
        await db.commit()
        await db.refresh(alert_instance)
        
        # Add to processing queue
        await self.alert_queue.put({
            'alert_id': alert_instance.id,
            'rule_id': result.rule_id,
            'severity': result.severity,
            'message': result.message,
            'labels': result.labels,
            'timestamp': datetime.utcnow()
        })
        
        logger.info(f"Generated alert {alert_instance.id} for rule {result.rule_id}")
        return alert_instance
    
    def _create_fingerprint(self, result: EvaluationResult) -> str:
        """Create unique fingerprint for alert instance."""
        import hashlib
        
        fingerprint_data = f"{result.rule_id}:{sorted(result.labels.items())}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    async def get_pending_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts waiting for processing."""
        alerts = []
        while not self.alert_queue.empty():
            try:
                alert = self.alert_queue.get_nowait()
                alerts.append(alert)
            except asyncio.QueueEmpty:
                break
        return alerts
