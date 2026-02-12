from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# SQLite does not support pool_size; use connect_args for SQLite
_connect_args = {}
_engine_args = {"echo": False}
if "sqlite" in settings.DATABASE_URL:
    _engine_args["connect_args"] = {"check_same_thread": False}
else:
    _engine_args["pool_size"] = 20
    _engine_args["max_overflow"] = 40

engine = create_async_engine(settings.DATABASE_URL, **_engine_args)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
