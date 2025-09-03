import redis.asyncio as redis
import json
import structlog
from typing import Optional, Dict, Any
from app.core.config import settings

logger = structlog.get_logger()

class RedisService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        
    async def connect(self):
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            await self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error("Redis connection failed", error=str(e))
            raise
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
    
    async def set_metric(self, key: str, value: Dict[str, Any], ttl: int = settings.REDIS_TTL):
        if not self.redis:
            return False
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
            await self.redis.publish("metrics_updates", json.dumps({"key": key, "value": value}))
            return True
        except Exception as e:
            logger.error("Redis set failed", key=key, error=str(e))
            return False
    
    async def get_metric(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.redis:
            return None
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error("Redis get failed", key=key, error=str(e))
            return None
    
    async def get_latest_metrics(self, pattern: str = "*", limit: int = 100) -> Dict[str, Any]:
        if not self.redis:
            return {}
        try:
            keys = await self.redis.keys(pattern)
            if not keys:
                return {}
            
            # Get values for keys (limited)
            limited_keys = keys[:limit]
            values = await self.redis.mget(limited_keys)
            
            result = {}
            for key, value in zip(limited_keys, values):
                if value:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        continue
            return result
        except Exception as e:
            logger.error("Redis get_latest_metrics failed", error=str(e))
            return {}
    
    async def health_check(self) -> bool:
        if not self.redis:
            return False
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False

redis_service = RedisService()
