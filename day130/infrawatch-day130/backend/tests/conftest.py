import pytest, pytest_asyncio, os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import get_db

TEST_DB_URL = "sqlite+aiosqlite:///./test_infrawatch.db"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    from app.models.models import Base as M
    async with engine.begin() as conn:
        await conn.run_sync(M.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(M.metadata.drop_all)
    await engine.dispose()
    if os.path.exists("test_infrawatch.db"):
        os.remove("test_infrawatch.db")

@pytest_asyncio.fixture
async def db_session(test_engine):
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(test_engine, db_session):
    from main import app
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async def override_get_db():
        async with factory() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
