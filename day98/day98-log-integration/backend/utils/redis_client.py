import redis.asyncio as redis
import os

_redis_client = None

async def get_redis_client():
    """Get Redis client singleton"""
    global _redis_client

    if _redis_client is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        _redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

    return _redis_client
