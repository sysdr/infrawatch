import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True
)

def get_redis():
    return redis_client
