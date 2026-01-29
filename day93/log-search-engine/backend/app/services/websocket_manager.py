from typing import Dict, Set, Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.search_subscriptions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
                if client_id in self.search_subscriptions:
                    del self.search_subscriptions[client_id]
    
    async def subscribe_to_search(self, client_id: str, query: str):
        """Subscribe client to real-time search updates"""
        self.search_subscriptions[client_id] = {
            "query": query,
            "subscribed_at": datetime.utcnow()
        }
    
    async def broadcast_new_log(self, log_data: Dict[str, Any]):
        """Broadcast new log to subscribed clients"""
        for client_id, subscription in self.search_subscriptions.items():
            if self._matches_query(log_data, subscription["query"]):
                await self._send_to_client(client_id, {
                    "type": "new_log",
                    "data": log_data
                })
    
    async def _send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected
            for conn in disconnected:
                self.active_connections[client_id].discard(conn)
    
    def _matches_query(self, log_data: Dict[str, Any], query: str) -> bool:
        """Simple query matching for real-time updates"""
        if not query:
            return True
        
        query_lower = query.lower()
        
        # Simple keyword matching
        searchable_text = f"{log_data.get('level', '')} {log_data.get('service', '')} {log_data.get('message', '')}".lower()
        
        return query_lower in searchable_text

ws_manager = WebSocketManager()
