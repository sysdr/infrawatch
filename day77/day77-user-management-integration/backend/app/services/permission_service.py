from sqlalchemy.orm import Session
from app.models import UserPermission, TeamPermission, TeamMember, PermissionType, AuditLog
from app.schemas.permission import UserPermissionCreate, TeamPermissionCreate
from app.services.team_service import TeamService
from app.core.redis_client import get_redis
from typing import List, Set
import json

class PermissionService:
    @staticmethod
    def grant_user_permission(db: Session, perm_data: UserPermissionCreate) -> UserPermission:
        permission = UserPermission(**perm_data.dict())
        db.add(permission)
        db.flush()
        
        # Log audit
        audit = AuditLog(
            user_id=perm_data.user_id,
            action="permission_granted",
            resource_type=perm_data.resource_type,
            resource_id=perm_data.resource_id,
            details={"permission": perm_data.permission_type.value}
        )
        db.add(audit)
        db.commit()
        db.refresh(permission)
        
        # Invalidate cache
        redis = get_redis()
        redis.delete(f"permissions:user:{perm_data.user_id}")
        
        return permission
    
    @staticmethod
    def grant_team_permission(db: Session, perm_data: TeamPermissionCreate) -> TeamPermission:
        permission = TeamPermission(**perm_data.dict())
        db.add(permission)
        db.flush()
        
        # Log audit
        audit = AuditLog(
            action="team_permission_granted",
            resource_type=perm_data.resource_type,
            resource_id=perm_data.resource_id,
            details={"team_id": perm_data.team_id, "permission": perm_data.permission_type.value}
        )
        db.add(audit)
        db.commit()
        db.refresh(permission)
        
        # Invalidate cache for all team members
        redis = get_redis()
        members = db.query(TeamMember).filter(TeamMember.team_id == perm_data.team_id).all()
        for member in members:
            redis.delete(f"permissions:user:{member.user_id}")
        
        return permission
    
    @staticmethod
    def check_permission(db: Session, user_id: int, resource_type: str, 
                        resource_id: str, permission_type: PermissionType) -> bool:
        """Check if user has permission (direct or inherited)"""
        
        # Check cache first
        redis = get_redis()
        cache_key = f"permissions:user:{user_id}:{resource_type}:{resource_id}:{permission_type.value}"
        cached = redis.get(cache_key)
        if cached:
            return cached == "1"
        
        # Check direct user permission
        direct_perm = db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.resource_type == resource_type,
            UserPermission.resource_id == resource_id,
            UserPermission.permission_type == permission_type
        ).first()
        
        if direct_perm:
            redis.setex(cache_key, 300, "1")  # Cache for 5 minutes
            return True
        
        # Check team permissions (including inherited)
        memberships = db.query(TeamMember).filter(TeamMember.user_id == user_id).all()
        
        for membership in memberships:
            # Get team hierarchy
            teams = TeamService.get_team_hierarchy(db, membership.team_id)
            
            for team in teams:
                team_perm = db.query(TeamPermission).filter(
                    TeamPermission.team_id == team.id,
                    TeamPermission.resource_type == resource_type,
                    TeamPermission.resource_id == resource_id,
                    TeamPermission.permission_type == permission_type
                ).first()
                
                if team_perm:
                    redis.setex(cache_key, 300, "1")
                    return True
        
        redis.setex(cache_key, 300, "0")
        return False
    
    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> List[dict]:
        """Get all effective permissions for a user"""
        permissions = set()
        
        # Direct permissions
        direct_perms = db.query(UserPermission).filter(
            UserPermission.user_id == user_id
        ).all()
        
        for perm in direct_perms:
            permissions.add((perm.resource_type, perm.resource_id, perm.permission_type.value, "direct"))
        
        # Team permissions
        memberships = db.query(TeamMember).filter(TeamMember.user_id == user_id).all()
        
        for membership in memberships:
            teams = TeamService.get_team_hierarchy(db, membership.team_id)
            
            for team in teams:
                team_perms = db.query(TeamPermission).filter(
                    TeamPermission.team_id == team.id
                ).all()
                
                for perm in team_perms:
                    permissions.add((
                        perm.resource_type, 
                        perm.resource_id, 
                        perm.permission_type.value,
                        f"team:{team.name}"
                    ))
        
        return [
            {
                "resource_type": p[0],
                "resource_id": p[1],
                "permission_type": p[2],
                "source": p[3]
            }
            for p in permissions
        ]
