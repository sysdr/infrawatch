import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisClient:
    _instance = None
    _redis = None
    
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._redis = await redis.from_url(REDIS_URL, decode_responses=True)
        return cls._redis
    
    @classmethod
    async def close(cls):
        if cls._redis:
            await cls._redis.close()

async def get_redis():
    """Redis dependency"""
    return await RedisClient.get_instance()
