import time
import json
from typing import Dict, Optional
from datetime import datetime, timedelta

class TokenBucketRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def is_allowed(self, identifier: str, max_requests: int = 10, window: int = 60) -> Dict:
        """
        Token bucket rate limiting implementation
        Returns dict with allowed status and metadata
        """
        key = f"rate_limit:{identifier}"
        now = time.time()
        
        # Get current bucket state
        bucket_data = await self.redis.get(key)
        
        if bucket_data:
            bucket = json.loads(bucket_data)
            tokens = bucket['tokens']
            last_refill = bucket['last_refill']
        else:
            tokens = max_requests
            last_refill = now
        
        # Calculate tokens to add based on time elapsed
        time_passed = now - last_refill
        tokens_to_add = int(time_passed * (max_requests / window))
        tokens = min(max_requests, tokens + tokens_to_add)
        
        # Check if request is allowed
        if tokens > 0:
            tokens -= 1
            allowed = True
        else:
            allowed = False
        
        # Update bucket state
        bucket_state = {
            'tokens': tokens,
            'last_refill': now,
            'max_requests': max_requests,
            'window': window
        }
        
        await self.redis.setex(key, window * 2, json.dumps(bucket_state))
        
        # Calculate retry after time
        retry_after = 0 if allowed else int(window / max_requests)
        
        return {
            'allowed': allowed,
            'tokens_remaining': tokens,
            'max_requests': max_requests,
            'window_seconds': window,
            'retry_after': retry_after,
            'reset_time': int(now + retry_after)
        }

    async def get_limit_status(self, identifier: str) -> Optional[Dict]:
        """Get current rate limit status for identifier"""
        key = f"rate_limit:{identifier}"
        bucket_data = await self.redis.get(key)
        
        if not bucket_data:
            return None
            
        bucket = json.loads(bucket_data)
        now = time.time()
        
        # Calculate current tokens
        time_passed = now - bucket['last_refill']
        tokens_to_add = int(time_passed * (bucket['max_requests'] / bucket['window']))
        current_tokens = min(bucket['max_requests'], bucket['tokens'] + tokens_to_add)
        
        return {
            'tokens_remaining': current_tokens,
            'max_requests': bucket['max_requests'],
            'window_seconds': bucket['window'],
            'last_refill': bucket['last_refill']
        }
