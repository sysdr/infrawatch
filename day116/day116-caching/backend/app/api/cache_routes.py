import time
from fastapi import APIRouter, HTTPException, Request
from app.cache.redis_cache import CacheManager, get_stats
from app.models import CacheSetRequest, InvalidateTagRequest, InvalidateKeyRequest

router = APIRouter(prefix="/api/cache", tags=["cache"])
def _cm(request: Request) -> CacheManager: return request.app.state.cache

@router.get("/get/{key}")
async def cache_get(key: str, request: Request):
    cache = _cm(request)
    start = time.perf_counter()
    value = await cache.get(key)
    return {"key": key, "value": value, "hit": value is not None, "latency_ms": round((time.perf_counter() - start) * 1000, 3)}

@router.post("/set")
async def cache_set(body: CacheSetRequest, request: Request):
    cache = _cm(request)
    ok = await cache.set(body.key, body.value, ttl=body.ttl, tags=body.tags or None) if body.strategy == "ttl" else await cache.write_behind(body.key, body.value, ttl=body.ttl, tags=body.tags or None)
    if not ok: raise HTTPException(500, "Cache write failed")
    return {"key": body.key, "strategy": body.strategy, "success": True}

@router.delete("/invalidate/tag")
async def invalidate_tag(body: InvalidateTagRequest, request: Request):
    return {"tag": body.tag, "keys_deleted": await _cm(request).invalidate_tag(body.tag)}

@router.delete("/invalidate/key")
async def invalidate_key(body: InvalidateKeyRequest, request: Request):
    return {"key": body.key, "deleted": await _cm(request).invalidate_key(body.key)}

@router.get("/keys")
async def list_keys(request: Request, pattern: str = "*", count: int = 50):
    keys = await _cm(request).list_keys(pattern=pattern, count=count)
    return {"keys": keys, "total": len(keys)}

@router.delete("/flush")
async def flush_cache(request: Request):
    await _cm(request).flush_all()
    return {"flushed": True}

@router.get("/stats")
async def cache_stats(request: Request):
    cache = _cm(request)
    return {**get_stats().to_dict(), "redis_info": await cache.get_redis_info(), "cdn": {"edge_hits": 0, "edge_misses": 0, "edge_hit_rate": 0, "edge_cache_entries": 0, "routes": []}}

@router.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    cache = _cm(request)
    key = f"user:{user_id}"
    cached = await cache.get(key)
    if cached: return {**cached, "source": "cache"}
    user = {"id": user_id, "name": f"User_{user_id}", "email": f"user{user_id}@example.com", "team_id": (user_id % 5) + 1, "role": "member"}
    await cache.set(key, user, ttl=300, tags=[f"user:{user_id}"])
    return {**user, "source": "db"}

@router.put("/users/{user_id}")
async def update_user(user_id: int, body: dict, request: Request):
    import asyncio
    cache = _cm(request)
    async def db_writer(v): await asyncio.sleep(0.005)
    await cache.write_through(f"user:{user_id}", {"id": user_id, **body}, db_writer=db_writer, ttl=300)
    return {"updated": True}

@router.get("/teams/{team_id}")
async def get_team(team_id: int, request: Request):
    cache = _cm(request)
    key = f"team:{team_id}:members"
    cached = await cache.get(key)
    if cached: return {**cached, "source": "cache"}
    team_data = {"team_id": team_id, "name": f"Team {team_id}", "members": []}
    await cache.set(key, team_data, ttl=120, tags=[f"team:{team_id}"])
    return {**team_data, "source": "db"}

@router.post("/simulate/burst")
async def simulate_burst(request: Request, count: int = 20):
    cache = _cm(request)
    results = []
    for uid in range(1, min(count + 1, 51)):
        key = f"user:{uid}"
        start = time.perf_counter()
        cached = await cache.get(key)
        lat = (time.perf_counter() - start) * 1000
        if not cached:
            await cache.set(key, {"id": uid, "name": f"User_{uid}", "team_id": (uid % 5) + 1}, ttl=300)
            results.append({"uid": uid, "hit": False, "latency_ms": round(lat, 2)})
        else:
            results.append({"uid": uid, "hit": True, "latency_ms": round(lat, 2)})
    return {"burst_results": results, "hit_rate": get_stats().hit_rate, "avg_latency_ms": get_stats().avg_latency_ms}
