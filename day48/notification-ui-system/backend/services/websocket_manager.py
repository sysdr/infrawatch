from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from user connections
        for user_id, connections in self.user_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.user_connections[user_id]
                break
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    def subscribe_user(self, websocket: WebSocket, user_id: str):
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        if websocket not in self.user_connections[user_id]:
            self.user_connections[user_id].append(websocket)
        
        logger.info(f"User {user_id} subscribed to notifications")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def broadcast_notification(self, notification: dict):
        """Broadcast notification to all connected clients or specific user"""
        message = {
            "type": "notification",
            "data": notification
        }
        
        user_id = notification.get("userId")
        
        if user_id and user_id in self.user_connections:
            # Send to specific user
            connections = self.user_connections[user_id].copy()
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    self.disconnect(connection)
        else:
            # Broadcast to all connections
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected websockets
            for connection in disconnected:
                self.disconnect(connection)
