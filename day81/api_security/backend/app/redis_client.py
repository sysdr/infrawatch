import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

class RedisClient:
    _instance = None
    
    def __init__(self):
        self.redis = None
    
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.redis = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._instance
    
    async def close(self):
        if self.redis:
            await self.redis.close()

async def get_redis():
    client = await RedisClient.get_instance()
    return client.redis
