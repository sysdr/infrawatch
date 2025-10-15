import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from ..models import Alert, AlertRule, AlertState

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, websocket_coordinator):
        self.websocket_coordinator = websocket_coordinator
        self.alerts: Dict[str, Alert] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.lock = asyncio.Lock()
        
    async def add_alert(self, alert: Alert):
        """Add new alert and broadcast update"""
        async with self.lock:
            self.alerts[alert.id] = alert
            await self._broadcast_alert_update(alert, "created")
    
    async def update_alert(self, alert: Alert):
        """Update existing alert and broadcast"""
        async with self.lock:
            self.alerts[alert.id] = alert
            await self._broadcast_alert_update(alert, "updated")
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get specific alert"""
        return self.alerts.get(alert_id)
    
    async def get_all_alerts(self) -> List[Alert]:
        """Get all alerts"""
        return list(self.alerts.values())
    
    async def get_firing_alerts(self) -> List[Alert]:
        """Get all currently firing alerts"""
        return [a for a in self.alerts.values() if a.state == AlertState.FIRING]
    
    async def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        async with self.lock:
            self.rules[rule.id] = rule
    
    async def get_all_rules(self) -> List[AlertRule]:
        """Get all rules"""
        return list(self.rules.values())
    
    async def _broadcast_alert_update(self, alert: Alert, action: str):
        """Broadcast alert state change to all WebSocket clients"""
        message = {
            "type": "alert_update",
            "action": action,
            "alert": alert.model_dump()
        }
        await self.websocket_coordinator.broadcast(message)
