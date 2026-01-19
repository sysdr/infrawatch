from fastapi import WebSocket
from typing import List, Dict, Any
import json
from datetime import datetime

class SecurityWebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_filters: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_filters[websocket] = {}
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_filters:
            del self.connection_filters[websocket]
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe_filters(self, websocket: WebSocket, filters: Dict[str, Any]):
        """Set filters for a specific connection"""
        self.connection_filters[websocket] = filters
    
    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to all connected clients matching filters"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                # Check if event matches connection filters
                filters = self.connection_filters.get(connection, {})
                if self._matches_filters(event, filters):
                    await connection.send_json(event)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    def _matches_filters(self, event: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if event matches filter criteria"""
        if not filters:
            return True
        
        # Check severity filter
        if "severity" in filters and event.get("severity") not in filters["severity"]:
            return False
        
        # Check event type filter
        if "event_type" in filters and event.get("event_type") not in filters["event_type"]:
            return False
        
        # Check minimum threat score
        if "min_threat_score" in filters and event.get("threat_score", 0) < filters["min_threat_score"]:
            return False
        
        return True
    
    async def disconnect_all(self):
        """Disconnect all active connections"""
        for connection in self.active_connections[:]:
            try:
                await connection.close()
            except:
                pass
            self.disconnect(connection)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
