import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from config.database import get_redis
import structlog

logger = structlog.get_logger()

class CacheService:
    def __init__(self):
        self.default_ttl = 300  # 5 minutes
        self.long_ttl = 3600    # 1 hour
        
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a unique cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}:{key_hash}"
    
    def _get_ttl(self, start_time: datetime, end_time: datetime) -> int:
        """Calculate appropriate TTL based on time range"""
        time_diff = end_time - start_time
        
        # Recent data (< 1 hour): shorter TTL
        if time_diff < timedelta(hours=1):
            return 60  # 1 minute
        # Medium range (< 24 hours): medium TTL
        elif time_diff < timedelta(days=1):
            return 300  # 5 minutes
        # Historical data: longer TTL
        else:
            return self.long_ttl
    
    async def get_query_result(self, metric_name: str, start_time: datetime, 
                              end_time: datetime, interval: str, 
                              aggregations: list) -> Optional[dict]:
        """Get cached query result"""
        try:
            redis_client = await get_redis()
            cache_key = self._generate_cache_key(
                "metrics_query",
                metric_name=metric_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                interval=interval,
                aggregations=sorted(aggregations)
            )
            
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.info("Cache hit", cache_key=cache_key)
                return json.loads(cached_data)
            
            logger.info("Cache miss", cache_key=cache_key)
            return None
            
        except Exception as e:
            logger.error("Cache get error", error=str(e))
            return None
    
    async def set_query_result(self, metric_name: str, start_time: datetime,
                              end_time: datetime, interval: str,
                              aggregations: list, data: dict) -> bool:
        """Cache query result"""
        try:
            redis_client = await get_redis()
            cache_key = self._generate_cache_key(
                "metrics_query",
                metric_name=metric_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                interval=interval,
                aggregations=sorted(aggregations)
            )
            
            ttl = self._get_ttl(start_time, end_time)
            data['cached_at'] = datetime.utcnow().isoformat()
            
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str)
            )
            
            logger.info("Cache set", cache_key=cache_key, ttl=ttl)
            return True
            
        except Exception as e:
            logger.error("Cache set error", error=str(e))
            return False
    
    async def invalidate_pattern(self, pattern: str) -> bool:
        """Invalidate cache entries matching pattern"""
        try:
            redis_client = await get_redis()
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
                logger.info("Cache invalidated", pattern=pattern, count=len(keys))
            return True
            
        except Exception as e:
            logger.error("Cache invalidation error", error=str(e))
            return False

cache_service = CacheService()
