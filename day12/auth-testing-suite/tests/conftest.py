import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_user_data():
    unique_email = f"test_{uuid4().hex}@example.com"
    return {
        "email": unique_email,
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.fixture
async def test_user(test_user_data):
    db = TestingSessionLocal()
    user = User(
        email=test_user_data["email"],
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"]
    )
    user.set_password(test_user_data["password"])
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close() 