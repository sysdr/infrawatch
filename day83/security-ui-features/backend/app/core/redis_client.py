import redis
import json
import os
from typing import Optional, Any

class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.redis_url, decode_responses=True)
    
    def set(self, key: str, value: Any, expiry: int = 3600):
        """Set value with optional expiry in seconds"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.setex(key, expiry, value)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value, auto-parse JSON if applicable"""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None
    
    def delete(self, key: str):
        """Delete key"""
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0
    
    def increment(self, key: str, amount: int = 1):
        """Increment counter"""
        return self.client.incrby(key, amount)
    
    def get_client(self):
        """Get raw Redis client"""
        return self.client

_redis_client = None

def get_redis_client() -> RedisClient:
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
