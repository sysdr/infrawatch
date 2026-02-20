import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.cache import CacheService
@pytest.fixture
def cache():
    return CacheService()
@pytest.mark.asyncio
async def test_cache_hit_increments_counter(cache):
    with patch("app.services.cache.get_redis") as mock_redis_factory:
        mock_r = AsyncMock()
        mock_r.get = AsyncMock(return_value='{"key": "value"}')
        mock_redis_factory.return_value = mock_r
        result = await cache.get("test_key")
        assert result == {"key": "value"}
        assert cache._hits == 1
        assert cache._misses == 0
@pytest.mark.asyncio
async def test_cache_miss_increments_misses(cache):
    with patch("app.services.cache.get_redis") as mock_redis_factory:
        mock_r = AsyncMock()
        mock_r.get = AsyncMock(return_value=None)
        mock_redis_factory.return_value = mock_r
        result = await cache.get("missing_key")
        assert result is None
        assert cache._misses == 1
def test_hit_rate_calculation(cache):
    cache._hits = 85
    cache._misses = 15
    assert cache.hit_rate == 85.0
