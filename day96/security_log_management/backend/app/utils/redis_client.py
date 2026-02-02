import redis
import os
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def cache_set(key: str, value: dict, expire: int = 3600):
    redis_client.setex(key, expire, json.dumps(value))

def cache_get(key: str):
    value = redis_client.get(key)
    return json.loads(value) if value else None

def cache_delete(key: str):
    redis_client.delete(key)

def increment_counter(key: str, window: int = 60):
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    result = pipe.execute()
    return result[0]
