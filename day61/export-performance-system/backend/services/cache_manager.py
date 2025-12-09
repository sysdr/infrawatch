import redis.asyncio as redis
import json
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'redis_hits': 0
        }
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using memory cache only.")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[str]:
        """Get from cache with L1 (memory) and L2 (Redis) tiers"""
        
        # L1: Memory cache
        if key in self.memory_cache:
            self.cache_stats['hits'] += 1
            self.cache_stats['memory_hits'] += 1
            logger.debug(f"Memory cache hit: {key}")
            return self.memory_cache[key]
        
        # L2: Redis cache
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats['hits'] += 1
                    self.cache_stats['redis_hits'] += 1
                    
                    # Promote to memory cache
                    if len(self.memory_cache) < 100:
                        self.memory_cache[key] = value
                    
                    logger.debug(f"Redis cache hit: {key}")
                    return value
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: str, ttl: int = 900):
        """Set in both memory and Redis cache"""
        
        # Set in memory cache
        if len(self.memory_cache) < 100:
            self.memory_cache[key] = value
        
        # Set in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(key, ttl, value)
                logger.debug(f"Cached in Redis: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.error(f"Redis set error: {e}")
    
    async def invalidate(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern"""
        count = 0
        
        # Clear memory cache
        keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k or pattern == "*"]
        for key in keys_to_remove:
            del self.memory_cache[key]
            count += 1
        
        # Clear Redis cache
        if self.redis_client:
            try:
                if pattern == "*":
                    await self.redis_client.flushdb()
                else:
                    cursor = 0
                    while True:
                        cursor, keys = await self.redis_client.scan(cursor, match=pattern)
                        if keys:
                            await self.redis_client.delete(*keys)
                            count += len(keys)
                        if cursor == 0:
                            break
            except Exception as e:
                logger.error(f"Redis invalidate error: {e}")
        
        logger.info(f"Invalidated {count} cache keys matching '{pattern}'")
        return count
    
    async def get_stats(self):
        """Get cache statistics"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        
        redis_info = {}
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                redis_info = {
                    'connected': True,
                    'used_memory_mb': info.get('used_memory', 0) / 1024 / 1024,
                    'total_keys': info.get('db0', {}).get('keys', 0) if 'db0' in info else 0
                }
            except:
                redis_info = {'connected': False}
        else:
            redis_info = {'connected': False}
        
        return {
            'hit_rate_percent': round(hit_rate, 2),
            'total_hits': self.cache_stats['hits'],
            'total_misses': self.cache_stats['misses'],
            'memory_hits': self.cache_stats['memory_hits'],
            'redis_hits': self.cache_stats['redis_hits'],
            'memory_cache_size': len(self.memory_cache),
            'redis': redis_info
        }
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
