import redis.asyncio as redis
import os
import json
from typing import Optional, Any

class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client: Optional[redis.Redis] = None
        self.default_ttl = 600  # 10 minutes
    
    async def connect(self):
        if not self.client:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self.client
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self.connect()
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        try:
            client = await self.connect()
            ttl = ttl or self.default_ttl
            await client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print(f"Redis set error: {e}")
            # Continue without caching if Redis fails
    
    async def delete(self, key: str):
        client = await self.connect()
        await client.delete(key)
    
    async def close(self):
        if self.client:
            await self.client.close()

redis_client = RedisClient()
