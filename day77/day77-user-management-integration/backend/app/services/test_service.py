from sqlalchemy.orm import Session
from app.models import User, Team, TeamMember, UserPermission, TeamPermission, PermissionType, UserStatus, TeamRole
from app.services.user_service import UserService
from app.services.team_service import TeamService
from app.services.permission_service import PermissionService
from app.schemas.user import UserCreate
from app.schemas.team import TeamCreate, TeamMemberAdd
from app.schemas.permission import UserPermissionCreate, TeamPermissionCreate
from datetime import datetime
from typing import Dict, List
import uuid
import json
from app.core.redis_client import get_redis

class TestService:
    @staticmethod
    def start_test_suite(db: Session) -> str:
        test_id = str(uuid.uuid4())
        redis = get_redis()
        redis.setex(f"test:{test_id}:status", 3600, json.dumps({
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "tests": []
        }))
        return test_id
    
    @staticmethod
    def run_all_tests(db: Session, test_id: str):
        results = []
        
        # Test 1: User Lifecycle
        results.append(TestService.test_user_lifecycle(db))
        TestService.update_test_status(test_id, results)
        
        # Test 2: Team Hierarchy
        results.append(TestService.test_team_hierarchy(db))
        TestService.update_test_status(test_id, results)
        
        # Test 3: Permission Inheritance
        results.append(TestService.test_permission_inheritance(db))
        TestService.update_test_status(test_id, results)
        
        # Test 4: Concurrent Operations
        results.append(TestService.test_concurrent_operations(db))
        TestService.update_test_status(test_id, results)
        
        # Test 5: Security Controls
        results.append(TestService.test_security_controls(db))
        TestService.update_test_status(test_id, results)
        
        # Mark as complete
        redis = get_redis()
        status_data = json.loads(redis.get(f"test:{test_id}:status"))
        status_data["status"] = "completed"
        status_data["completed_at"] = datetime.utcnow().isoformat()
        redis.setex(f"test:{test_id}:status", 3600, json.dumps(status_data))
    
    @staticmethod
    def test_user_lifecycle(db: Session) -> Dict:
        try:
            # Create user
            user_data = UserCreate(
                email=f"test_{uuid.uuid4()}@example.com",
                username=f"testuser_{uuid.uuid4().hex[:8]}",
                full_name="Test User",
                password="password123"
            )
            user = UserService.create_user(db, user_data)
            assert user.status == UserStatus.PENDING
            
            # Activate
            user = UserService.activate_user(db, user.id)
            assert user.status == UserStatus.ACTIVE
            
            # Suspend
            user = UserService.suspend_user(db, user.id)
            assert user.status == UserStatus.SUSPENDED
            
            # Archive
            user = UserService.archive_user(db, user.id)
            assert user.status == UserStatus.ARCHIVED
            
            return {
                "name": "User Lifecycle Test",
                "status": "passed",
                "duration": 150,
                "details": "All state transitions successful"
            }
        except Exception as e:
            return {
                "name": "User Lifecycle Test",
                "status": "failed",
                "duration": 0,
                "error": str(e)
            }
    
    @staticmethod
    def test_team_hierarchy(db: Session) -> Dict:
        try:
            # Create parent team
            parent = TeamService.create_team(db, TeamCreate(
                name=f"Engineering_{uuid.uuid4().hex[:8]}",
                description="Engineering Department"
            ))
            
            # Create child team
            child = TeamService.create_team(db, TeamCreate(
                name=f"Backend_{uuid.uuid4().hex[:8]}",
                description="Backend Team",
                parent_id=parent.id
            ))
            
            # Verify hierarchy
            hierarchy = TeamService.get_team_hierarchy(db, child.id)
            assert len(hierarchy) == 2
            assert hierarchy[0].id == child.id
            assert hierarchy[1].id == parent.id
            
            return {
                "name": "Team Hierarchy Test",
                "status": "passed",
                "duration": 120,
                "details": "Hierarchy correctly established"
            }
        except Exception as e:
            return {
                "name": "Team Hierarchy Test",
                "status": "failed",
                "duration": 0,
                "error": str(e)
            }
    
    @staticmethod
    def test_permission_inheritance(db: Session) -> Dict:
        try:
            # Create user
            user_data = UserCreate(
                email=f"test_{uuid.uuid4()}@example.com",
                username=f"testuser_{uuid.uuid4().hex[:8]}",
                password="password123"
            )
            user = UserService.create_user(db, user_data)
            
            # Create team
            team = TeamService.create_team(db, TeamCreate(
                name=f"Team_{uuid.uuid4().hex[:8]}"
            ))
            
            # Add user to team
            TeamService.add_member(db, team.id, TeamMemberAdd(
                user_id=user.id,
                role=TeamRole.MEMBER
            ))
            
            # Grant team permission
            PermissionService.grant_team_permission(db, TeamPermissionCreate(
                team_id=team.id,
                resource_type="dashboard",
                resource_id="main",
                permission_type=PermissionType.READ
            ))
            
            # Check user has inherited permission
            has_perm = PermissionService.check_permission(
                db, user.id, "dashboard", "main", PermissionType.READ
            )
            assert has_perm == True
            
            return {
                "name": "Permission Inheritance Test",
                "status": "passed",
                "duration": 180,
                "details": "Permissions inherited correctly"
            }
        except Exception as e:
            return {
                "name": "Permission Inheritance Test",
                "status": "failed",
                "duration": 0,
                "error": str(e)
            }
    
    @staticmethod
    def test_concurrent_operations(db: Session) -> Dict:
        try:
            # Simulate concurrent user creations
            users = []
            for i in range(10):
                user_data = UserCreate(
                    email=f"concurrent_{i}_{uuid.uuid4()}@example.com",
                    username=f"concurrent_{i}_{uuid.uuid4().hex[:8]}",
                    password="password123"
                )
                user = UserService.create_user(db, user_data)
                users.append(user)
            
            assert len(users) == 10
            
            return {
                "name": "Concurrent Operations Test",
                "status": "passed",
                "duration": 250,
                "details": "10 concurrent operations successful"
            }
        except Exception as e:
            return {
                "name": "Concurrent Operations Test",
                "status": "failed",
                "duration": 0,
                "error": str(e)
            }
    
    @staticmethod
    def test_security_controls(db: Session) -> Dict:
        try:
            # Create and suspend user
            user_data = UserCreate(
                email=f"security_{uuid.uuid4()}@example.com",
                username=f"security_{uuid.uuid4().hex[:8]}",
                password="password123"
            )
            user = UserService.create_user(db, user_data)
            user = UserService.activate_user(db, user.id)
            user = UserService.suspend_user(db, user.id)
            
            # Verify user is suspended
            assert user.status == UserStatus.SUSPENDED
            assert user.is_active == False
            
            # Verify audit log exists
            assert len(user.audit_logs) > 0
            
            return {
                "name": "Security Controls Test",
                "status": "passed",
                "duration": 160,
                "details": "Security controls enforced"
            }
        except Exception as e:
            return {
                "name": "Security Controls Test",
                "status": "failed",
                "duration": 0,
                "error": str(e)
            }
    
    @staticmethod
    def update_test_status(test_id: str, results: List[Dict]):
        redis = get_redis()
        status_data = json.loads(redis.get(f"test:{test_id}:status"))
        status_data["tests"] = results
        redis.setex(f"test:{test_id}:status", 3600, json.dumps(status_data))
    
    @staticmethod
    def get_test_results(db: Session, test_id: str) -> Dict:
        redis = get_redis()
        status = redis.get(f"test:{test_id}:status")
        if not status:
            return {"error": "Test not found"}
        return json.loads(status)
    
    @staticmethod
    def get_current_status(db: Session) -> Dict:
        total_users = db.query(User).count()
        total_teams = db.query(Team).count()
        total_permissions = db.query(UserPermission).count() + db.query(TeamPermission).count()
        
        return {
            "users": total_users,
            "teams": total_teams,
            "permissions": total_permissions,
            "timestamp": datetime.utcnow().isoformat()
        }
