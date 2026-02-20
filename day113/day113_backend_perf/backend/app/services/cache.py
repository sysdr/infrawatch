import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import get_settings
settings = get_settings()
logger = logging.getLogger(__name__)
_redis: Optional[aioredis.Redis] = None
async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis
class CacheService:
    def __init__(self):
        self._hits = 0
        self._misses = 0
    async def get(self, key: str) -> Optional[Any]:
        r = await get_redis()
        try:
            raw = await r.get(key)
            if raw is not None:
                self._hits += 1
                return json.loads(raw)
            self._misses += 1
            return None
        except Exception as e:
            logger.warning(f"Cache GET error for {key}: {e}")
            self._misses += 1
            return None
    async def set(self, key: str, value: Any, ttl: int = None, tags: list[str] = None):
        r = await get_redis()
        ttl = ttl or settings.CACHE_DEFAULT_TTL
        try:
            serialised = json.dumps(value, default=str)
            await r.setex(key, ttl, serialised)
            if tags:
                pipe = r.pipeline()
                for tag in tags:
                    tag_key = f"cache_tag:{tag}"
                    pipe.sadd(tag_key, key)
                    pipe.expire(tag_key, ttl + 60)
                await pipe.execute()
        except Exception as e:
            logger.warning(f"Cache SET error for {key}: {e}")
    async def delete(self, key: str):
        r = await get_redis()
        await r.delete(key)
    async def delete_by_tag(self, tag: str):
        r = await get_redis()
        tag_key = f"cache_tag:{tag}"
        keys = await r.smembers(tag_key)
        if keys:
            pipe = r.pipeline()
            for k in keys:
                pipe.delete(k)
            pipe.delete(tag_key)
            await pipe.execute()
        return len(keys)
    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return round((self._hits / total) * 100, 1) if total > 0 else 0.0
    @property
    def stats(self) -> dict:
        return {"hits": self._hits, "misses": self._misses, "hit_rate_pct": self.hit_rate}
cache_service = CacheService()
