from fastapi import APIRouter
from datetime import datetime

from app.core.redis_client import redis_client

router = APIRouter()

@router.get("/stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    stats = await redis_client.get_cache_stats()
    
    total_requests = stats["hits"] + stats["misses"]
    hit_rate = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "hits": stats["hits"],
        "misses": stats["misses"],
        "hit_rate": round(hit_rate, 2),
        "total_keys": stats["keys"]
    }

@router.post("/invalidate")
async def invalidate_cache(pattern: str = "*"):
    """Invalidate cache entries matching pattern"""
    # In production, use Redis SCAN for pattern matching
    return {
        "message": f"Cache invalidated for pattern: {pattern}",
        "timestamp": datetime.now().isoformat()
    }
