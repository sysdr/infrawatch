import redis.asyncio as redis
import os
import json

class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None
    
    async def connect(self):
        if not self.client:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self.client
    
    async def get(self, key):
        client = await self.connect()
        return await client.get(key)
    
    async def set(self, key, value, ex=None):
        client = await self.connect()
        return await client.set(key, value, ex=ex)
    
    async def zadd(self, key, mapping):
        client = await self.connect()
        return await client.zadd(key, mapping)
    
    async def zrange(self, key, start, end):
        client = await self.connect()
        return await client.zrange(key, start, end)
    
    async def hincrby(self, key, field, amount=1):
        client = await self.connect()
        return await client.hincrby(key, field, amount)
    
    async def hgetall(self, key):
        client = await self.connect()
        return await client.hgetall(key)

redis_client = RedisClient()
