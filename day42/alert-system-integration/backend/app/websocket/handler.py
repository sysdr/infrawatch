import asyncio
import json
import logging
import websockets

logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self, coordinator, state_manager):
        self.coordinator = coordinator
        self.state_manager = state_manager
    
    async def handle_connection(self, websocket, path):
        """Handle individual WebSocket connection"""
        await self.coordinator.register(websocket)
        
        try:
            # Send initial state
            alerts = await self.state_manager.get_all_alerts()
            initial_message = {
                "type": "initial_state",
                "alerts": [alert.dict() for alert in alerts]
            }
            await websocket.send(json.dumps(initial_message))
            
            # Keep connection alive
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(websocket, data)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        finally:
            await self.coordinator.unregister(websocket)
    
    async def _handle_message(self, websocket, data: dict):
        """Handle incoming WebSocket messages"""
        msg_type = data.get("type")
        
        if msg_type == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
        elif msg_type == "get_alerts":
            alerts = await self.state_manager.get_all_alerts()
            await websocket.send(json.dumps({
                "type": "alerts",
                "data": [alert.dict() for alert in alerts]
            }))
