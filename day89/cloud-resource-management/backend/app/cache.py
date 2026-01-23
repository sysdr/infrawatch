import json
import os
from typing import Any, Optional

class _DictCache:
    def __init__(self):
        self._store = {}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def set(self, key: str, value: Any, expire: int = 300):
        self._store[key] = value

    def delete(self, key: str):
        self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self._store

    def increment(self, key: str, amount: int = 1) -> int:
        v = self._store.get(key, 0) + amount
        self._store[key] = v
        return v

    def get_keys(self, pattern: str):
        return [k for k in self._store if pattern.replace("*", "") in k]

def _make_cache():
    try:
        import redis
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True,
            socket_connect_timeout=1,
        )
        r.ping()
    except Exception:
        return _DictCache()

    class RedisCache:
        def __init__(self, client):
            self.redis_client = client

        def get(self, key: str) -> Optional[Any]:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None

        def set(self, key: str, value: Any, expire: int = 300):
            self.redis_client.setex(key, expire, json.dumps(value))

        def delete(self, key: str):
            self.redis_client.delete(key)

        def exists(self, key: str) -> bool:
            return self.redis_client.exists(key) > 0

        def increment(self, key: str, amount: int = 1) -> int:
            return self.redis_client.incrby(key, amount)

        def get_keys(self, pattern: str):
            return self.redis_client.keys(pattern)

    return RedisCache(r)

cache = _make_cache()
