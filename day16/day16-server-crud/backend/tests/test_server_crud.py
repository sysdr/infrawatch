import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import uuid

# Set up test database before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import app after setting up test database
from app.core.database import get_db, Base
from app.models import server, audit

def setup_test_db():
    """Set up test database tables"""
    server.Base.metadata.create_all(bind=engine)
    audit.Base.metadata.create_all(bind=engine)

def cleanup_test_db():
    """Clean up test database"""
    if os.path.exists("test.db"):
        os.remove("test.db")

# Clean up any existing test database
cleanup_test_db()
setup_test_db()

# Now import the app
from app.main import app

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_server():
    # Use unique name to avoid conflicts
    unique_name = f"test-server-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/servers/",
        json={
            "name": unique_name,
            "hostname": "test.example.com",
            "ip_address": "192.168.1.100",
            "server_type": "web",
            "environment": "test",
            "region": "us-east-1",
            "tenant_id": "test-tenant"
        }
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == unique_name
    assert data["status"] == "active"

def test_list_servers():
    response = client.get("/api/servers/")
    assert response.status_code == 200
    data = response.json()
    assert "servers" in data
    assert "total" in data

def test_get_server():
    # First create a server with unique name
    unique_name = f"get-test-server-{uuid.uuid4().hex[:8]}"
    create_response = client.post(
        "/api/servers/",
        json={
            "name": unique_name,
            "hostname": "get-test.example.com",
            "ip_address": "192.168.1.101",
            "tenant_id": "test-tenant"
        }
    )
    server_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/servers/{server_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == unique_name

def test_update_server():
    # First create a server with unique name
    unique_name = f"update-test-server-{uuid.uuid4().hex[:8]}"
    create_response = client.post(
        "/api/servers/",
        json={
            "name": unique_name,
            "hostname": "update-test.example.com",
            "ip_address": "192.168.1.102",
            "tenant_id": "test-tenant"
        }
    )
    server_id = create_response.json()["id"]
    
    # Then update it
    response = client.put(
        f"/api/servers/{server_id}",
        json={"status": "maintenance"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "maintenance"

def test_delete_server():
    # First create a server with unique name
    unique_name = f"delete-test-server-{uuid.uuid4().hex[:8]}"
    create_response = client.post(
        "/api/servers/",
        json={
            "name": unique_name,
            "hostname": "delete-test.example.com",
            "ip_address": "192.168.1.103",
            "tenant_id": "test-tenant"
        }
    )
    server_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/api/servers/{server_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "decommissioned"
