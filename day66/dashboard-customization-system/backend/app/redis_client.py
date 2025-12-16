import redis
import os
import json
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

class CacheService:
    @staticmethod
    def get_dashboard(dashboard_id: str, version: int) -> Optional[dict]:
        key = f"dashboard:{dashboard_id}:v{version}"
        cached = redis_client.get(key)
        return json.loads(cached) if cached else None
    
    @staticmethod
    def set_dashboard(dashboard_id: str, version: int, data: dict, ttl: int = 300):
        key = f"dashboard:{dashboard_id}:v{version}"
        redis_client.setex(key, ttl, json.dumps(data))
    
    @staticmethod
    def invalidate_dashboard(dashboard_id: str):
        pattern = f"dashboard:{dashboard_id}:v*"
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
    
    @staticmethod
    def set_user_presence(dashboard_id: str, user_id: str, ttl: int = 30):
        key = f"dashboard:{dashboard_id}:users"
        redis_client.sadd(key, user_id)
        redis_client.expire(key, ttl)
    
    @staticmethod
    def get_active_users(dashboard_id: str) -> set:
        key = f"dashboard:{dashboard_id}:users"
        return redis_client.smembers(key) or set()
    
    @staticmethod
    def remove_user_presence(dashboard_id: str, user_id: str):
        key = f"dashboard:{dashboard_id}:users"
        redis_client.srem(key, user_id)
