import json
import time
import asyncio
from typing import Any, Optional
from dataclasses import dataclass, field
import redis.asyncio as aioredis
from redis.asyncio import Redis

@dataclass
class CacheStats:
    hits: int = 0; misses: int = 0; invalidations: int = 0; sets: int = 0
    latencies: list = field(default_factory=list)
    @property
    def hit_rate(self) -> float:
        t = self.hits + self.misses
        return round(self.hits / t * 100, 2) if t > 0 else 0.0
    @property
    def avg_latency_ms(self) -> float:
        return round(sum(self.latencies[-100:]) / len(self.latencies[-100:]), 3) if self.latencies else 0.0
    def to_dict(self) -> dict:
        return {"hits": self.hits, "misses": self.misses, "invalidations": self.invalidations, "sets": self.sets, "hit_rate": self.hit_rate, "avg_latency_ms": self.avg_latency_ms}

_stats = CacheStats()
def get_stats() -> CacheStats: return _stats

class CacheManager:
    TAG_PREFIX = "tag:"
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._client: Optional[Redis] = None
    async def connect(self):
        self._client = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        await self._client.ping()
    async def disconnect(self):
        if self._client: await self._client.aclose()
    @property
    def client(self) -> Redis:
        if not self._client: raise RuntimeError("Not connected")
        return self._client
    async def get(self, key: str) -> Optional[Any]:
        start = time.perf_counter()
        try:
            raw = await self.client.get(key)
            elapsed = (time.perf_counter() - start) * 1000
            _stats.latencies.append(elapsed)
            if raw is None: _stats.misses += 1; return None
            _stats.hits += 1
            return json.loads(raw)
        except Exception: _stats.misses += 1; return None
    async def set(self, key: str, value: Any, ttl: int = 300, tags: list[str] | None = None) -> bool:
        try:
            pipe = self.client.pipeline()
            pipe.setex(key, ttl, json.dumps(value, default=str))
            if tags:
                for tag in tags:
                    pipe.sadd(f"{self.TAG_PREFIX}{tag}", key)
                    pipe.expire(f"{self.TAG_PREFIX}{tag}", ttl + 60)
            await pipe.execute()
            _stats.sets += 1
            return True
        except Exception: return False
    async def delete(self, key: str) -> bool:
        try: return (await self.client.delete(key)) > 0
        except Exception: return False
    async def write_through(self, key: str, value: Any, db_writer, ttl: int = 300, tags: list[str] | None = None) -> bool:
        await db_writer(value); await self.set(key, value, ttl=ttl, tags=tags); return True
    async def write_behind(self, key: str, value: Any, queue_name: str = "write_behind_queue", ttl: int = 60, tags: list[str] | None = None) -> bool:
        await self.set(key, value, ttl=ttl, tags=tags)
        await self.client.lpush(queue_name, json.dumps({"key": key, "value": value, "ts": time.time()}))
        return True
    async def invalidate_tag(self, tag: str) -> int:
        tag_key = f"{self.TAG_PREFIX}{tag}"
        members = await self.client.smembers(tag_key)
        if not members: return 0
        for k in members: await self.client.delete(k)
        await self.client.delete(tag_key)
        _stats.invalidations += len(members)
        return len(members)
    async def invalidate_key(self, key: str) -> bool:
        r = await self.client.delete(key)
        if r: _stats.invalidations += 1
        return bool(r)
    async def list_keys(self, pattern: str = "*", count: int = 100) -> list[dict]:
        entries = []
        async for key in self.client.scan_iter(match=pattern, count=50):
            if key.startswith(self.TAG_PREFIX): continue
            ttl = await self.client.ttl(key)
            entries.append({"key": key, "ttl": ttl, "size_bytes": 0})
            if len(entries) >= count: break
        return entries
    async def get_redis_info(self) -> dict:
        info = await self.client.info()
        return {"used_memory_human": info.get("used_memory_human", "N/A"), "connected_clients": info.get("connected_clients", 0)}
    async def flush_all(self) -> bool: await self.client.flushdb(); return True
