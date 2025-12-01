from typing import Optional, Any, Callable
from database.redis_config import cache_get, cache_set, cache_delete
import hashlib
import json

class CacheManager:
    """Manage caching for analytics queries"""
    
    @staticmethod
    def generate_cache_key(prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"
    
    @staticmethod
    async def get_or_compute(
        key: str,
        compute_fn: Callable,
        ttl: int = 60
    ) -> Any:
        """Get from cache or compute and cache"""
        # Try cache first
        cached = await cache_get(key)
        if cached is not None:
            return cached
        
        # Compute value
        value = await compute_fn()
        
        # Cache result
        await cache_set(key, value, ttl)
        
        return value
    
    @staticmethod
    async def invalidate_pattern(pattern: str):
        """Invalidate all keys matching pattern"""
        # In production, use Redis SCAN with pattern matching
        pass
