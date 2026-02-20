from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings
settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, pool_size=settings.DB_POOL_SIZE, max_overflow=settings.DB_MAX_OVERFLOW, pool_pre_ping=settings.DB_POOL_PRE_PING, pool_recycle=settings.DB_POOL_RECYCLE, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
class Base(DeclarativeBase):
    pass
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
async def get_pool_stats() -> dict:
    pool = engine.pool
    return {"pool_size": pool.size(), "checked_in": pool.checkedin(), "checked_out": pool.checkedout(), "overflow": pool.overflow(), "utilisation_pct": round((pool.checkedout() / max(pool.size() + pool.overflow(), 1)) * 100, 1)}
