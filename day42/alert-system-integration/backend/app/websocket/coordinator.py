import asyncio
import json
import logging
from datetime import datetime
from typing import Set
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

class WebSocketCoordinator:
    def __init__(self):
        self.connections: Set[WebSocketServerProtocol] = set()
        self.lock = asyncio.Lock()
    
    async def register(self, websocket: WebSocketServerProtocol):
        """Register new WebSocket connection"""
        async with self.lock:
            self.connections.add(websocket)
            logger.info(f"Client connected. Total connections: {len(self.connections)}")
    
    async def unregister(self, websocket: WebSocketServerProtocol):
        """Unregister WebSocket connection"""
        async with self.lock:
            self.connections.discard(websocket)
            logger.info(f"Client disconnected. Total connections: {len(self.connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.connections:
            return
        
        message["timestamp"] = datetime.now().isoformat()
        message_str = json.dumps(message)
        
        async with self.lock:
            disconnected = set()
            for websocket in self.connections:
                try:
                    await websocket.send(message_str)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.connections.discard(websocket)
