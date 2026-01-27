"""Redis client configuration"""
import structlog

logger = structlog.get_logger()

async def init_redis():
    """Initialize Redis connection"""
    logger.info("redis_initialized")
