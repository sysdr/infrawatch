import time
from fastapi import APIRouter
from app.cache.redis_cache import get_stats
router = APIRouter(prefix="/api/metrics", tags=["metrics"])
@router.get("")
async def get_metrics(): return {"timestamp": time.time(), **get_stats().to_dict()}
