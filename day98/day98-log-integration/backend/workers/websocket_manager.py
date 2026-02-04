from fastapi import WebSocket
from typing import Dict, Set
import asyncio
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, Dict] = {}
        self.connection_filters: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[websocket] = {
            "connected_at": asyncio.get_event_loop().time(),
            "messages_sent": 0
        }
        asyncio.create_task(self._keepalive(websocket))

    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
        if websocket in self.connection_filters:
            del self.connection_filters[websocket]

    async def set_filters(self, websocket: WebSocket, filters: Dict):
        self.connection_filters[websocket] = filters

    async def broadcast(self, message: Dict, filters: Dict = None):
        disconnected = []
        for websocket in self.active_connections:
            if self._matches_filters(message, self.connection_filters.get(websocket, {})):
                try:
                    await websocket.send_json(message)
                    self.active_connections[websocket]["messages_sent"] += 1
                except Exception:
                    disconnected.append(websocket)
        for websocket in disconnected:
            await self.disconnect(websocket)

    def _matches_filters(self, message: Dict, filters: Dict) -> bool:
        if not filters:
            return True
        for key, value in filters.items():
            if message.get(key) != value:
                return False
        return True

    async def _keepalive(self, websocket: WebSocket):
        try:
            while websocket in self.active_connections:
                await asyncio.sleep(30)
                await websocket.send_json({"type": "ping"})
        except Exception:
            await self.disconnect(websocket)
