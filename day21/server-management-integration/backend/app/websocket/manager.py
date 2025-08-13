from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "message": "WebSocket connection established"
        }, websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[Any, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[Any, Any]):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn)

    async def send_server_update(self, server_data: Dict[Any, Any]):
        message = {
            "type": "server_update",
            "data": server_data,
            "timestamp": server_data.get("updated_at")
        }
        await self.broadcast(message)

    async def send_server_created(self, server_data: Dict[Any, Any]):
        message = {
            "type": "server_created",
            "data": server_data,
            "timestamp": server_data.get("created_at")
        }
        await self.broadcast(message)

    async def send_server_deleted(self, server_id: int):
        message = {
            "type": "server_deleted",
            "data": {"id": server_id},
            "timestamp": None
        }
        await self.broadcast(message)
