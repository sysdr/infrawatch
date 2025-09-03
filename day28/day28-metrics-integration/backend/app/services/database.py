from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.models.metrics import Base
import structlog

logger = structlog.get_logger()

class DatabaseService:
    def __init__(self):
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.MAX_CONNECTIONS - settings.POOL_SIZE,
            echo=False
        )
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created")
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e))
            logger.warning("Application will continue without database tables")
    
    async def get_session(self):
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error("Database session error", error=str(e))
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        try:
            async with self.async_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False

db_service = DatabaseService()
