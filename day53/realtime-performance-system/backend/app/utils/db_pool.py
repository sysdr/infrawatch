import asyncpg
import os
from typing import Optional
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def create_pool(self):
        """Create connection pool with optimized settings"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                dsn=os.getenv("DATABASE_URL"),
                min_size=int(os.getenv("POOL_MIN_SIZE", 10)),
                max_size=int(os.getenv("POOL_MAX_SIZE", 100)),
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=30
            )
            logger.info(f"Database pool created: min={os.getenv('POOL_MIN_SIZE')}, max={os.getenv('POOL_MAX_SIZE')}")
        return self.pool
    
    async def close_pool(self):
        """Close all connections in pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Async context manager that yields a database connection."""
        if self.pool is None:
            await self.create_pool()
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)

db_pool = DatabasePool()
