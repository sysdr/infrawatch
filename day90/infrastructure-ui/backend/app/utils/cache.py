import redis.asyncio as redis
from app.config import settings
import json
from typing import Optional

class CacheManager:
    def __init__(self):
        self.redis_client = None
    
    async def connect(self):
        self.redis_client = await redis.from_url(settings.redis_url)
    
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Optional[dict]:
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except:
            return None
    
    async def set(self, key: str, value: dict, ttl: int = 300):
        if not self.redis_client:
            return
        try:
            await self.redis_client.setex(key, ttl, json.dumps(value))
        except:
            pass
    
    async def delete(self, key: str):
        if not self.redis_client:
            return
        try:
            await self.redis_client.delete(key)
        except:
            pass

cache_manager = CacheManager()
