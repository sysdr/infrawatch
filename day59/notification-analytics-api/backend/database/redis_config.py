import redis.asyncio as redis
import os
import json
from typing import Optional, Any

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    r = await get_redis()
    value = await r.get(key)
    if value:
        return json.loads(value)
    return None

async def cache_set(key: str, value: Any, ttl: int = 60):
    """Set value in cache with TTL"""
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value, default=str))

async def cache_delete(key: str):
    """Delete value from cache"""
    r = await get_redis()
    await r.delete(key)
