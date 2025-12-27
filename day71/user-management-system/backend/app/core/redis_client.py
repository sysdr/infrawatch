import redis.asyncio as redis
from redis.exceptions import RedisError
from .config import settings
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.connected: bool = False
    
    async def connect(self):
        try:
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
            # Test connection
            await self.redis.ping()
            self.connected = True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.connected = False
            self.redis = None
    
    async def disconnect(self):
        if self.redis:
            try:
            await self.redis.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self.redis = None
                self.connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis or not self.connected:
            return None
        try:
        value = await self.redis.get(f"{settings.CACHE_PREFIX}:{key}")
        if value:
            return json.loads(value)
        except (RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Redis get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, expire: int = None):
        if not self.redis or not self.connected:
            return
        try:
        expire = expire or settings.CACHE_EXPIRE_SECONDS
        await self.redis.setex(
            f"{settings.CACHE_PREFIX}:{key}",
            expire,
            json.dumps(value)
        )
        except (RedisError, TypeError) as e:
            logger.warning(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        if not self.redis or not self.connected:
            return
        try:
        await self.redis.delete(f"{settings.CACHE_PREFIX}:{key}")
        except RedisError as e:
            logger.warning(f"Redis delete error: {e}")

redis_client = RedisClient()
