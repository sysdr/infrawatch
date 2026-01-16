import time
import uuid
from typing import Tuple
from app.config import get_settings

settings = get_settings()

class RateLimiter:
    
    @staticmethod
    async def check_rate_limit(
        redis_client,
        api_key_id: str,
        limit: int = None,
        window: int = None
    ) -> Tuple[bool, dict]:
        """
        Token bucket rate limiting algorithm
        Returns: (allowed, info_dict)
        """
        limit = limit or settings.rate_limit_requests
        window = window or settings.rate_limit_window
        
        bucket_key = f"rate_limit:{api_key_id}"
        now = time.time()
        window_start = now - window
        
        # Remove old tokens outside the time window
        await redis_client.zremrangebyscore(bucket_key, 0, window_start)
        
        # Count current tokens
        current_count = await redis_client.zcard(bucket_key)
        
        if current_count < limit:
            # Add new token
            token_id = str(uuid.uuid4())
            await redis_client.zadd(bucket_key, {token_id: now})
            await redis_client.expire(bucket_key, window + 10)  # Add buffer
            
            remaining = limit - current_count - 1
            
            return True, {
                "allowed": True,
                "limit": limit,
                "remaining": remaining,
                "reset_at": int(now + window)
            }
        else:
            # Rate limit exceeded
            # Get oldest token to calculate reset time
            oldest_tokens = await redis_client.zrange(bucket_key, 0, 0, withscores=True)
            if oldest_tokens:
                oldest_time = oldest_tokens[0][1]
                reset_at = int(oldest_time + window)
            else:
                reset_at = int(now + window)
            
            return False, {
                "allowed": False,
                "limit": limit,
                "remaining": 0,
                "reset_at": reset_at,
                "retry_after": reset_at - int(now)
            }
    
    @staticmethod
    async def get_rate_limit_info(redis_client, api_key_id: str, limit: int, window: int) -> dict:
        """Get current rate limit status without consuming a token"""
        bucket_key = f"rate_limit:{api_key_id}"
        now = time.time()
        window_start = now - window
        
        # Clean old tokens
        await redis_client.zremrangebyscore(bucket_key, 0, window_start)
        
        # Count current tokens
        current_count = await redis_client.zcard(bucket_key)
        remaining = max(0, limit - current_count)
        
        return {
            "limit": limit,
            "remaining": remaining,
            "window": window,
            "reset_at": int(now + window)
        }
