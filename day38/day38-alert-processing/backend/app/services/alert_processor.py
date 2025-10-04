import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from sqlalchemy import select
from ..models.alert import Alert, AlertState, AlertSeverity
from ..models.database import get_db_session
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

class AlertProcessor:
    def __init__(self, websocket_manager=None):
        self.running = False
        self.processing_queue = asyncio.Queue()
        self.websocket_manager = websocket_manager
        self.auto_resolution_rules = {
            AlertSeverity.CRITICAL: timedelta(minutes=30),
            AlertSeverity.HIGH: timedelta(minutes=15),
            AlertSeverity.MEDIUM: timedelta(minutes=10),
            AlertSeverity.LOW: timedelta(minutes=5)
        }
        
    async def start(self):
        """Start the alert processing engine"""
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self._process_alerts())
        asyncio.create_task(self._auto_resolution_worker())
        logger.info("Alert processor started")
    
    async def stop(self):
        """Stop the alert processing engine"""
        self.running = False
        logger.info("Alert processor stopped")
    
    def is_running(self) -> bool:
        return self.running
    
    async def process_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """Process incoming alert and manage lifecycle"""
        try:
            # Create alert instance
            alert = Alert(
                id=alert_data.get('id'),
                title=alert_data['title'],
                description=alert_data.get('description', ''),
                metric_name=alert_data['metric_name'],
                current_value=alert_data['current_value'],
                threshold_value=alert_data['threshold_value'],
                service_name=alert_data.get('service_name', 'unknown'),
                state=AlertState.NEW,
                created_at=datetime.utcnow()
            )
            
            # Classify severity
            alert.severity = await self._classify_severity(alert)
            
            # Check for duplicates and deduplication
            existing_alert = await self._check_duplicate(alert)
            if existing_alert:
                await self._update_duplicate_alert(existing_alert, alert)
                return existing_alert
            
            # Save to database
            async with get_db_session() as session:
                session.add(alert)
                await session.commit()
                await session.refresh(alert)
            
            # Add to processing queue
            await self.processing_queue.put(alert)
            
            # Notify via websocket
            if self.websocket_manager:
                await self.websocket_manager.broadcast_alert(alert.to_dict())
            
            logger.info(f"Alert processed: {alert.id} - {alert.severity}")
            return alert
            
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
            raise
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Alert:
        """Acknowledge an alert manually"""
        async with get_db_session() as session:
            alert = await session.get(Alert, alert_id)
            if not alert:
                raise ValueError(f"Alert {alert_id} not found")
            
            if alert.state != AlertState.NEW:
                raise ValueError(f"Alert {alert_id} is not in NEW state")
            
            alert.state = AlertState.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
            
            await session.commit()
            await session.refresh(alert)
            
            # Notify via websocket
            if self.websocket_manager:
                await self.websocket_manager.broadcast_alert(alert.to_dict())
            
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return alert
    
    async def resolve_alert(self, alert_id: str, resolved_by: str = None, auto_resolved: bool = False) -> Alert:
        """Resolve an alert"""
        async with get_db_session() as session:
            alert = await session.get(Alert, alert_id)
            if not alert:
                raise ValueError(f"Alert {alert_id} not found")
            
            if alert.state == AlertState.RESOLVED:
                return alert
            
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = resolved_by if not auto_resolved else "auto-resolution"
            alert.auto_resolved = auto_resolved
            
            await session.commit()
            await session.refresh(alert)
            
            # Notify via websocket
            if self.websocket_manager:
                await self.websocket_manager.broadcast_alert(alert.to_dict())
            
            resolution_type = "auto-resolved" if auto_resolved else "manually resolved"
            logger.info(f"Alert {resolution_type}: {alert_id}")
            return alert
    
    async def _classify_severity(self, alert: Alert) -> AlertSeverity:
        """Classify alert severity based on multiple factors"""
        # Base severity from threshold breach
        severity_score = 0
        
        # Threshold breach magnitude
        if alert.current_value > alert.threshold_value:
            breach_ratio = alert.current_value / alert.threshold_value
            if breach_ratio > 2.0:
                severity_score += 30
            elif breach_ratio > 1.5:
                severity_score += 20
            else:
                severity_score += 10
        
        # Service criticality
        critical_services = ['database', 'payment', 'auth', 'api-gateway']
        if alert.service_name.lower() in critical_services:
            severity_score += 25
        
        # Time of day factor
        current_hour = datetime.utcnow().hour
        if 9 <= current_hour <= 17:  # Business hours
            severity_score += 10
        
        # Historical frequency
        frequency_score = await self._get_historical_frequency_score(alert)
        severity_score += frequency_score
        
        # Determine severity based on total score
        if severity_score >= 50:
            return AlertSeverity.CRITICAL
        elif severity_score >= 35:
            return AlertSeverity.HIGH
        elif severity_score >= 20:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    async def _get_historical_frequency_score(self, alert: Alert) -> int:
        """Calculate frequency score based on historical data"""
        # In real implementation, query historical alerts
        # For now, return a mock score
        return 5
    
    async def _check_duplicate(self, alert: Alert) -> Optional[Alert]:
        """Check for duplicate alerts"""
        async with get_db_session() as session:
            # Look for similar alerts in last 10 minutes using SQLAlchemy 2.0 async syntax
            cutoff_time = datetime.utcnow() - timedelta(minutes=10)
            
            existing = await session.execute(
                select(Alert).where(
                    Alert.metric_name == alert.metric_name,
                    Alert.service_name == alert.service_name,
                    Alert.state != AlertState.RESOLVED,
                    Alert.created_at > cutoff_time
                ).order_by(Alert.created_at.desc()).limit(1)
            )
            
            result = existing.scalar_one_or_none()
            return result
    
    async def _update_duplicate_alert(self, existing_alert: Alert, new_alert: Alert):
        """Update existing alert with new data"""
        existing_alert.current_value = new_alert.current_value
        existing_alert.last_updated = datetime.utcnow()
        existing_alert.occurrence_count = getattr(existing_alert, 'occurrence_count', 1) + 1
    
    async def _process_alerts(self):
        """Background worker to process alerts"""
        while self.running:
            try:
                alert = await asyncio.wait_for(
                    self.processing_queue.get(), 
                    timeout=1.0
                )
                
                # Process alert lifecycle
                await self._handle_alert_lifecycle(alert)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in alert processing worker: {str(e)}")
    
    async def _handle_alert_lifecycle(self, alert: Alert):
        """Handle alert lifecycle transitions"""
        # Auto-escalation for critical alerts
        if alert.severity == AlertSeverity.CRITICAL and alert.state == AlertState.NEW:
            # Schedule escalation if not acknowledged within 15 minutes
            asyncio.create_task(
                self._schedule_escalation(alert.id, timedelta(minutes=15))
            )
        
        # Set auto-resolution timer
        resolution_time = self.auto_resolution_rules.get(
            alert.severity, 
            timedelta(minutes=10)
        )
        
        asyncio.create_task(
            self._schedule_auto_resolution(alert.id, resolution_time)
        )
    
    async def _schedule_escalation(self, alert_id: str, delay: timedelta):
        """Schedule alert escalation"""
        await asyncio.sleep(delay.total_seconds())
        
        async with get_db_session() as session:
            alert = await session.get(Alert, alert_id)
            if alert and alert.state == AlertState.NEW:
                # Escalate alert (notify manager, increase severity, etc.)
                logger.info(f"Escalating unacknowledged alert: {alert_id}")
    
    async def _schedule_auto_resolution(self, alert_id: str, delay: timedelta):
        """Schedule automatic alert resolution"""
        await asyncio.sleep(delay.total_seconds())
        
        async with get_db_session() as session:
            alert = await session.get(Alert, alert_id)
            if alert and alert.state != AlertState.RESOLVED:
                # Check if conditions have improved
                if await self._should_auto_resolve(alert):
                    await self.resolve_alert(alert_id, auto_resolved=True)
    
    async def _should_auto_resolve(self, alert: Alert) -> bool:
        """Determine if alert should be auto-resolved"""
        # In real implementation, check current metric values
        # For demo, auto-resolve after delay
        return True
    
    async def _auto_resolution_worker(self):
        """Background worker for auto-resolution logic"""
        while self.running:
            try:
                await self._check_auto_resolution_candidates()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in auto-resolution worker: {str(e)}")
    
    async def _check_auto_resolution_candidates(self):
        """Check for alerts that can be auto-resolved"""
        async with get_db_session() as session:
            # Find alerts that have been in acknowledged state too long
            cutoff_time = datetime.utcnow() - timedelta(hours=2)
            
            candidates = await session.execute(
                select(Alert).where(
                    Alert.state == AlertState.ACKNOWLEDGED,
                    Alert.acknowledged_at < cutoff_time
                )
            )
            
            alert_objects = candidates.scalars().all()
            for alert in alert_objects:
                if await self._should_auto_resolve_by_id(alert.id):
                    await self.resolve_alert(alert.id, auto_resolved=True)
    
    async def _should_auto_resolve_by_id(self, alert_id: str) -> bool:
        """Check if specific alert should be auto-resolved"""
        # In real implementation, check current conditions
        return True
