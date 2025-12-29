from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from app.config import settings
import json
import asyncio

class TeamWebSocketManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.redis_client = None
    
    async def get_redis(self):
        if not self.redis_client:
            self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client
    
    async def connect(self, websocket: WebSocket, team_id: int, user_id: int):
        await websocket.accept()
        
        if team_id not in self.active_connections:
            self.active_connections[team_id] = {}
        
        self.active_connections[team_id][user_id] = websocket
        
        # Subscribe to Redis channel
        redis_client = await self.get_redis()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"team:{team_id}:events")
        
        # Start listening task
        asyncio.create_task(self._listen_redis(pubsub, team_id))
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "team_id": team_id,
            "message": "Connected to team channel"
        })
    
    def disconnect(self, team_id: int, user_id: int):
        if team_id in self.active_connections:
            self.active_connections[team_id].pop(user_id, None)
            if not self.active_connections[team_id]:
                del self.active_connections[team_id]
    
    async def _listen_redis(self, pubsub, team_id: int):
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await self.broadcast_to_team(team_id, data)
    
    async def broadcast_to_team(self, team_id: int, message: dict):
        if team_id in self.active_connections:
            disconnected = []
            for user_id, connection in self.active_connections[team_id].items():
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(user_id)
            
            for user_id in disconnected:
                self.disconnect(team_id, user_id)

manager = TeamWebSocketManager()
