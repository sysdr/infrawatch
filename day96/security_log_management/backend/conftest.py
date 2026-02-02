"""Pytest configuration: use SQLite for DB; mock Redis if unavailable."""
import os

# Set before any app import so DB uses SQLite for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# If Redis is not available, patch it before app is imported
try:
    import redis as _redis_mod
    _r = _redis_mod.from_url(os.environ["REDIS_URL"], decode_responses=True)
    _r.ping()
except Exception:
    import redis as _redis_mod
    import unittest.mock as mock
    _fake_redis = mock.MagicMock()
    _pipe = mock.MagicMock()
    _pipe.incr.return_value = _pipe
    _pipe.expire.return_value = _pipe
    _pipe.execute.return_value = [1]
    _fake_redis.pipeline.return_value = _pipe
    _fake_redis.get.return_value = None
    _fake_redis.setex.return_value = None
    _fake_redis.delete.return_value = None
    _redis_mod.from_url = lambda *a, **kw: _fake_redis
