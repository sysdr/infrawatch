import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis

from app.main import app, get_db
from app.models import Base
from app.models.permission_models import User, Role, Team, PermissionPolicy, UserRole, TeamMember, Resource

# Test database - use PostgreSQL (same as production)
import os
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://rbac_user:rbac_pass@postgres:5432/rbac_test_db")
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def setup_database():
    """Setup test data."""
    db = TestingSessionLocal()
    
    # Create test user
    user = User(id=1, username="testuser", email="test@example.com", hashed_password="hashed")
    db.add(user)
    
    # Create test role
    role = Role(id=1, name="engineer", description="Engineering role")
    db.add(role)
    
    # Create test team
    team = Team(id=1, name="backend-team", description="Backend team")
    db.add(team)
    
    # Assign user to role
    user_role = UserRole(user_id=1, role_id=1)
    db.add(user_role)
    
    # Add user to team
    team_member = TeamMember(team_id=1, user_id=1)
    db.add(team_member)
    
    # Create test resource
    resource = Resource(resource_type="project", resource_id="42", owner_id=1)
    db.add(resource)
    
    # Create test policies
    policy1 = PermissionPolicy(
        name="engineer-read-policy",
        subject_type="role",
        subject_id="1",
        action="read",
        resource_type="project",
        resource_id="*",
        effect="allow",
        priority=10
    )
    db.add(policy1)
    
    policy2 = PermissionPolicy(
        name="team-write-policy",
        subject_type="team",
        subject_id="1",
        action="write",
        resource_type="project",
        resource_id="42",
        effect="allow",
        priority=20
    )
    db.add(policy2)
    
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_permission_evaluation_allowed(setup_database):
    """Test permission check that should be allowed."""
    response = client.post("/api/permissions/evaluate", json={
        "subject_id": "user:1",
        "action": "read",
        "resource_type": "project",
        "resource_id": "42"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] == True

def test_permission_evaluation_denied(setup_database):
    """Test permission check that should be denied."""
    response = client.post("/api/permissions/evaluate", json={
        "subject_id": "user:1",
        "action": "delete",
        "resource_type": "project",
        "resource_id": "99"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] == False

def test_resource_owner_access(setup_database):
    """Test that resource owner has full access."""
    response = client.post("/api/permissions/evaluate", json={
        "subject_id": "user:1",
        "action": "delete",
        "resource_type": "project",
        "resource_id": "42"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] == True
    assert "owner" in data["policy_matched"]

def test_create_policy():
    """Test creating new policy."""
    response = client.post("/api/policies", json={
        "name": "test-policy",
        "subject_type": "user",
        "subject_id": "1",
        "action": "admin",
        "resource_type": "dashboard",
        "resource_id": "*",
        "effect": "allow",
        "priority": 50
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-policy"

def test_audit_logging(setup_database):
    """Test that permission checks generate audit events."""
    # Make permission check
    client.post("/api/permissions/evaluate", json={
        "subject_id": "user:1",
        "action": "read",
        "resource_type": "project",
        "resource_id": "42"
    })
    
    # Check audit log
    response = client.get("/api/audit/events?limit=1")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    assert events[0]["action"] == "read"

def test_audit_stats(setup_database):
    """Test audit statistics endpoint."""
    # Generate some events
    for i in range(5):
        client.post("/api/permissions/evaluate", json={
            "subject_id": "user:1",
            "action": "read",
            "resource_type": "project",
            "resource_id": "42"
        })
    
    response = client.get("/api/audit/stats?time_range_hours=24")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_checks"] >= 5

def test_compliance_check():
    """Test compliance violation detection."""
    response = client.post("/api/compliance/check")
    assert response.status_code == 200
    data = response.json()
    assert "violations_found" in data
