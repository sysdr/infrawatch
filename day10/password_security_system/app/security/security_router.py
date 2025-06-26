from fastapi import APIRouter, Depends, Request, HTTPException
from slowapi.util import get_remote_address
import redis.asyncio as redis
from app.security.lockout_manager import AccountLockoutManager
from app.security.rate_limiter import TokenBucketRateLimiter

router = APIRouter()

async def get_redis(request: Request) -> redis.Redis:
    """Dependency to get Redis client from app state"""
    return request.app.state.redis

@router.get("/lockout-status/{identifier}")
async def get_lockout_status(
    identifier: str,
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get account lockout status for debugging/monitoring"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    lockout_manager = AccountLockoutManager(redis_client)
    status = await lockout_manager.get_lockout_status(identifier)
    return status

@router.get("/rate-limit-status")
async def get_rate_limit_status(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get rate limit status for current client"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    client_ip = get_remote_address(request)
    rate_limiter = TokenBucketRateLimiter(redis_client)
    
    statuses = {}
    for endpoint in ['login', 'register', 'reset']:
        status = await rate_limiter.get_limit_status(f"{endpoint}:{client_ip}")
        if status:
            statuses[endpoint] = status
    
    return statuses
