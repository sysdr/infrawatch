import redis.asyncio as redis
from app.core.config import settings

async def get_redis_client():
    """Create Redis client"""
    return await redis.from_url(settings.REDIS_URL, decode_responses=True)
