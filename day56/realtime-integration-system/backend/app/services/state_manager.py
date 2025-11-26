from typing import Dict, Any, List
from datetime import datetime
import asyncio
import structlog

logger = structlog.get_logger()

class StateManager:
    """Manages application state and synchronization"""
    
    def __init__(self):
        self.state_versions: Dict[str, int] = {}
        self.state_deltas: Dict[str, List[Dict]] = {}
        self.current_version = 0
        self.pending_notifications: List[Dict] = []
    
    async def get_current_version(self) -> int:
        """Get current global state version"""
        return self.current_version
    
    async def get_delta(self, client_id: str, from_version: int) -> Dict[str, Any]:
        """Get state changes since version"""
        delta_events = []
        
        # Get all events after from_version
        if client_id in self.state_deltas:
            delta_events = [
                event for event in self.state_deltas[client_id]
                if event["version"] > from_version
            ]
        
        return {
            "events": delta_events,
            "version": self.current_version
        }
    
    async def add_state_change(self, client_id: str, change: Dict[str, Any]):
        """Record state change"""
        self.current_version += 1
        
        event = {
            "version": self.current_version,
            "change": change,
            "timestamp": datetime.now().isoformat()
        }
        
        if client_id not in self.state_deltas:
            self.state_deltas[client_id] = []
        
        self.state_deltas[client_id].append(event)
        
        # Keep only last 100 events
        if len(self.state_deltas[client_id]) > 100:
            self.state_deltas[client_id] = self.state_deltas[client_id][-100:]
    
    async def queue_notification(self, notification: Dict[str, Any]):
        """Queue notification for retry"""
        self.pending_notifications.append({
            "notification": notification,
            "queued_at": datetime.now().isoformat()
        })
