import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from security.rate_limiter import RateLimiter
from unittest.mock import AsyncMock, MagicMock
import time

@pytest.mark.asyncio
async def test_rate_limit_allows_within_quota():
    redis_mock = AsyncMock()
    redis_mock.zremrangebyscore = AsyncMock()
    redis_mock.zcard = AsyncMock(return_value=50)  # 50 existing tokens
    redis_mock.zadd = AsyncMock()
    redis_mock.expire = AsyncMock()
    
    allowed, info = await RateLimiter.check_rate_limit(
        redis_mock, "test_key", limit=100, window=60
    )
    
    assert allowed is True
    assert info["allowed"] is True
    assert info["limit"] == 100
    assert info["remaining"] == 49  # 100 - 50 - 1
    assert "reset_at" in info

@pytest.mark.asyncio
async def test_rate_limit_blocks_over_quota():
    redis_mock = AsyncMock()
    redis_mock.zremrangebyscore = AsyncMock()
    redis_mock.zcard = AsyncMock(return_value=100)  # At limit
    redis_mock.zrange = AsyncMock(return_value=[(b"token1", time.time() - 30)])
    
    allowed, info = await RateLimiter.check_rate_limit(
        redis_mock, "test_key", limit=100, window=60
    )
    
    assert allowed is False
    assert info["allowed"] is False
    assert info["remaining"] == 0
    assert "retry_after" in info
