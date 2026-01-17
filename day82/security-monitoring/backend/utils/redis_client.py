"""Redis client configuration"""
from redis import asyncio as aioredis
import os

_redis_client = None

async def get_redis_client():
    """Get Redis client instance"""
    global _redis_client
    
    if _redis_client is None:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        # Use decode_responses=False for streams to get bytes
        # This works better with xread operations
        _redis_client = await aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=False  # Keep as bytes for stream operations
        )
    
    return _redis_client
