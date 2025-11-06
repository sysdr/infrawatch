import redis.asyncio as redis
from app.core.config import settings
import json

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def get_preference_cache(self, user_id: str):
        if not self.redis:
            return None
        try:
            key = f"pref:{user_id}"
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    
    async def set_preference_cache(self, user_id: str, preferences: dict, ttl: int = 300):
        if not self.redis:
            return
        try:
            key = f"pref:{user_id}"
            await self.redis.setex(key, ttl, json.dumps(preferences))
        except Exception:
            pass
    
    async def circuit_breaker_is_open(self, channel: str) -> bool:
        if not self.redis:
            return False
        try:
            key = f"circuit:{channel}"
            return await self.redis.exists(key) > 0
        except Exception:
            return False
    
    async def open_circuit_breaker(self, channel: str, duration: int = 30):
        if not self.redis:
            return
        try:
            key = f"circuit:{channel}"
            await self.redis.setex(key, duration, "open")
        except Exception:
            pass
    
    async def close(self):
        if self.redis:
            await self.redis.close()

redis_client = RedisClient()
