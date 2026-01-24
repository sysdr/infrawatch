from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast to all connected clients"""
        for client_connections in self.active_connections.values():
            for connection in client_connections:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def send_to_subscriptions(self, resource_ids: list, message: dict):
        """Send message to clients subscribed to specific resources"""
        for client_id, connections in self.active_connections.items():
            # In production, track per-client subscriptions
            for connection in connections:
                try:
                    await connection.send_json(message)
                except:
                    pass

ws_manager = WebSocketManager()
