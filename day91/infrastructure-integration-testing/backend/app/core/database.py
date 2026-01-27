"""Database configuration"""
import structlog

logger = structlog.get_logger()

async def init_db():
    """Initialize database connection"""
    logger.info("database_initialized")
