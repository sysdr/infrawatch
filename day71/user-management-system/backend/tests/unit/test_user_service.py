import pytest
from app.services.user_service import user_service
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = await user_service.create_user(db, user_data)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.hashed_password != "password123"
    assert user.profile is not None
    assert user.preferences is not None

@pytest.mark.asyncio
async def test_authenticate_user_success(db):
    # Create user first
    user_data = UserCreate(email="auth@example.com", password="testpass123")
    await user_service.create_user(db, user_data)
    
    # Authenticate
    authenticated = await user_service.authenticate_user(db, "auth@example.com", "testpass123")
    assert authenticated is not None
    assert authenticated.email == "auth@example.com"

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db):
    user_data = UserCreate(email="wrong@example.com", password="correctpass")
    await user_service.create_user(db, user_data)
    
    authenticated = await user_service.authenticate_user(db, "wrong@example.com", "wrongpass")
    assert authenticated is None
