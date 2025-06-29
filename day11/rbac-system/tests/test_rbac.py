import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from src.main import app
from src.database.config import get_engine, Base, get_session_local
from sqlalchemy.orm import sessionmaker
from src.models.user import User, Role, Permission
from src.auth.utils import get_password_hash, get_user_permissions
import os

# Use a separate test database
os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/rbac_test"

# Use the same session creation pattern as the main app
from src.database.config import get_session_local

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
def test_db():
    """Create and clean up test database for each test"""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=get_engine())
    # Create tables
    Base.metadata.create_all(bind=get_engine())
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        # Create test permissions with unique names
        permissions = [
            Permission(name="read_logs", description="Read log entries", resource="logs", action="read"),
            Permission(name="write_logs", description="Write log entries", resource="logs", action="write"),
            Permission(name="manage_users", description="Manage users", resource="users", action="manage"),
            Permission(name="manage_roles", description="Manage roles", resource="roles", action="manage"),
            Permission(name="manage_permissions", description="Manage permissions", resource="permissions", action="manage"),
        ]
        
        for permission in permissions:
            db.add(permission)
        
        # Create test roles with unique names
        admin_role = Role(name="test_admin", description="Administrator role", is_active=True)
        user_role = Role(name="test_user", description="Regular user role", is_active=True)
        
        # Assign permissions to roles before committing
        admin_role.permissions = permissions
        user_role.permissions = [permissions[0]]  # Only read_logs
        db.add(admin_role)
        db.add(user_role)
        db.commit()
        
        # Create test users with unique emails
        admin_user = User(
            email="test_admin@test.com",
            username="test_admin",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        regular_user = User(
            email="test_user@test.com", 
            username="test_user",
            hashed_password=get_password_hash("user123"),
            is_active=True
        )
        
        admin_user.roles = [admin_role]
        regular_user.roles = [user_role]
        
        db.add(admin_user)
        db.add(regular_user)
        db.commit()
        db.refresh(admin_user)
        db.refresh(regular_user)
        
        yield db
        
    finally:
        db.close()
        # Clean up tables after each test
        Base.metadata.drop_all(bind=get_engine())

@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration"""
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"

@pytest.mark.asyncio
async def test_login_user(client, test_db):
    """Test user login"""
    response = await client.post("/api/v1/auth/login", data={
        "username": "test_admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(client, test_db):
    """Test getting current user info"""
    # Login first
    login_response = await client.post("/api/v1/auth/login", data={
        "username": "test_admin",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # Get user info
    response = await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_admin"
    assert "manage_users" in data["permissions"]

@pytest.mark.asyncio
async def test_admin_access_control(client, test_db):
    """Test admin access control"""
    # Login as regular user
    login_response = await client.post("/api/v1/auth/login", data={
        "username": "test_user", 
        "password": "user123"
    })
    user_token = login_response.json()["access_token"]
    
    # Try to access admin endpoint (should fail)
    response = await client.get("/api/v1/admin/users", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert response.status_code == 403
    
    # Login as admin
    admin_login = await client.post("/api/v1/auth/login", data={
        "username": "test_admin",
        "password": "admin123"
    })
    admin_token = admin_login.json()["access_token"]
    
    # Access admin endpoint (should succeed)
    response = await client.get("/api/v1/admin/users", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_permission_checking(client, test_db):
    """Test permission-based access control"""
    # Login as admin
    login_response = await client.post("/api/v1/auth/login", data={
        "username": "test_admin",
        "password": "admin123"
    })
    admin_token = login_response.json()["access_token"]
    
    # Create a new permission
    response = await client.post("/api/v1/admin/permissions", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "test_permission_new",
            "description": "Test permission",
            "resource": "test",
            "action": "test"
        }
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_role_creation(client, test_db):
    """Test role creation and assignment"""
    # Login as admin
    login_response = await client.post("/api/v1/auth/login", data={
        "username": "test_admin",
        "password": "admin123"
    })
    admin_token = login_response.json()["access_token"]
    
    # Create a new role
    response = await client.post("/api/v1/admin/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "test_role_new",
            "description": "Test role",
            "permission_ids": [1, 2]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_role_new"

if __name__ == "__main__":
    pytest.main([__file__])
