from typing import Dict, List, Set, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import redis
import json
import hashlib

from ..models.permission_models import PermissionPolicy, User, Role, Team, UserRole, TeamMember, Resource

class PermissionEngine:
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes
    
    def evaluate(self, subject_id: str, action: str, resource_type: str, 
                 resource_id: str, context: Dict = None) -> tuple[bool, str, str]:
        """
        Evaluate permission request.
        Returns: (allowed: bool, reason: str, policy_matched: str)
        """
        # Check cache first
        cache_key = self._cache_key(subject_id, action, resource_type, resource_id)
        cached = self.redis.get(cache_key)
        if cached:
            result = json.loads(cached)
            return result['allowed'], result['reason'], result['policy']
        
        # Get all applicable policies
        policies = self._get_applicable_policies(subject_id, action, resource_type, resource_id)
        
        # Evaluate policies by priority (explicit deny wins)
        explicit_deny = None
        explicit_allow = None
        
        for policy in sorted(policies, key=lambda p: p.priority, reverse=True):
            # Check conditions
            if policy.conditions:
                if not self._evaluate_conditions(policy.conditions, context or {}):
                    continue
            
            if policy.effect == 'deny':
                explicit_deny = policy
                break  # Deny always wins
            elif policy.effect == 'allow':
                if not explicit_allow:
                    explicit_allow = policy
        
        # Make decision
        if explicit_deny:
            result = (False, "Explicit deny policy", explicit_deny.name)
        elif explicit_allow:
            result = (True, "Explicit allow policy", explicit_allow.name)
        else:
            result = (False, "No matching policy (implicit deny)", "default-deny")
        
        # Cache result
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps({
                'allowed': result[0],
                'reason': result[1],
                'policy': result[2]
            })
        )
        
        return result
    
    def _get_applicable_policies(self, subject_id: str, action: str, 
                                 resource_type: str, resource_id: str) -> List[PermissionPolicy]:
        """Get all policies that might apply to this request."""
        policies = []
        
        # Parse subject_id (format: "user:123" or "role:admin" or "team:5")
        subject_type, sid = subject_id.split(':', 1)
        
        # Direct policies for this subject
        direct_policies = self.db.query(PermissionPolicy).filter(
            PermissionPolicy.subject_type == subject_type,
            PermissionPolicy.subject_id == sid,
            PermissionPolicy.action.in_([action, '*']),
            PermissionPolicy.resource_type == resource_type
        ).filter(
            (PermissionPolicy.resource_id == resource_id) |
            (PermissionPolicy.resource_id == '*') |
            (PermissionPolicy.resource_id == None)
        ).all()
        
        policies.extend(direct_policies)
        
        # If subject is user, get inherited policies from roles and teams
        if subject_type == 'user':
            user_id = int(sid)
            
            # Get user's roles (with inheritance)
            role_ids = self._get_user_roles_recursive(user_id)
            for role_id in role_ids:
                role_policies = self.db.query(PermissionPolicy).filter(
                    PermissionPolicy.subject_type == 'role',
                    PermissionPolicy.subject_id == str(role_id),
                    PermissionPolicy.action.in_([action, '*']),
                    PermissionPolicy.resource_type == resource_type
                ).filter(
                    (PermissionPolicy.resource_id == resource_id) |
                    (PermissionPolicy.resource_id == '*') |
                    (PermissionPolicy.resource_id == None)
                ).all()
                policies.extend(role_policies)
            
            # Get user's teams (with inheritance)
            team_ids = self._get_user_teams_recursive(user_id)
            for team_id in team_ids:
                team_policies = self.db.query(PermissionPolicy).filter(
                    PermissionPolicy.subject_type == 'team',
                    PermissionPolicy.subject_id == str(team_id),
                    PermissionPolicy.action.in_([action, '*']),
                    PermissionPolicy.resource_type == resource_type
                ).filter(
                    (PermissionPolicy.resource_id == resource_id) |
                    (PermissionPolicy.resource_id == '*') |
                    (PermissionPolicy.resource_id == None)
                ).all()
                policies.extend(team_policies)
            
            # Check resource ownership
            resource = self.db.query(Resource).filter(
                Resource.resource_type == resource_type,
                Resource.resource_id == resource_id
            ).first()
            if resource and resource.owner_id == user_id:
                # Owners get full access (create synthetic policy)
                owner_policy = PermissionPolicy(
                    name="resource-owner-policy",
                    subject_type="user",
                    subject_id=sid,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    effect="allow",
                    priority=1000  # Highest priority
                )
                policies.append(owner_policy)
        
        return policies
    
    def _get_user_roles_recursive(self, user_id: int, visited: Set[int] = None) -> Set[int]:
        """Get all roles for user including inherited roles."""
        if visited is None:
            visited = set()
        
        role_ids = set()
        
        # Get direct roles
        user_roles = self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
        for ur in user_roles:
            if ur.role_id not in visited:
                visited.add(ur.role_id)
                role_ids.add(ur.role_id)
                
                # Get parent roles
                role = self.db.query(Role).filter(Role.id == ur.role_id).first()
                if role and role.parent_role_id and role.parent_role_id not in visited:
                    parent_roles = self._get_parent_roles(role.parent_role_id, visited)
                    role_ids.update(parent_roles)
        
        return role_ids
    
    def _get_parent_roles(self, role_id: int, visited: Set[int]) -> Set[int]:
        """Get all parent roles recursively."""
        if role_id in visited:
            return set()  # Cycle detection
        
        visited.add(role_id)
        role_ids = {role_id}
        
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role and role.parent_role_id:
            parent_roles = self._get_parent_roles(role.parent_role_id, visited)
            role_ids.update(parent_roles)
        
        return role_ids
    
    def _get_user_teams_recursive(self, user_id: int, visited: Set[int] = None) -> Set[int]:
        """Get all teams for user including parent teams."""
        if visited is None:
            visited = set()
        
        team_ids = set()
        
        # Get direct teams
        memberships = self.db.query(TeamMember).filter(TeamMember.user_id == user_id).all()
        for tm in memberships:
            if tm.team_id not in visited:
                visited.add(tm.team_id)
                team_ids.add(tm.team_id)
                
                # Get parent teams
                team = self.db.query(Team).filter(Team.id == tm.team_id).first()
                if team and team.parent_team_id and team.parent_team_id not in visited:
                    parent_teams = self._get_parent_teams(team.parent_team_id, visited)
                    team_ids.update(parent_teams)
        
        return team_ids
    
    def _get_parent_teams(self, team_id: int, visited: Set[int]) -> Set[int]:
        """Get all parent teams recursively."""
        if team_id in visited:
            return set()  # Cycle detection
        
        visited.add(team_id)
        team_ids = {team_id}
        
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if team and team.parent_team_id:
            parent_teams = self._get_parent_teams(team.parent_team_id, visited)
            team_ids.update(parent_teams)
        
        return team_ids
    
    def _evaluate_conditions(self, conditions: Dict, context: Dict) -> bool:
        """Evaluate policy conditions against request context."""
        # Time-based conditions
        if 'time_range' in conditions:
            current_hour = datetime.utcnow().hour
            start, end = conditions['time_range']
            if not (start <= current_hour < end):
                return False
        
        # Approval requirements
        if conditions.get('requires_approval') and not context.get('approval_granted'):
            return False
        
        # IP restrictions
        if 'allowed_ips' in conditions:
            if context.get('ip_address') not in conditions['allowed_ips']:
                return False
        
        return True
    
    def _cache_key(self, subject_id: str, action: str, resource_type: str, resource_id: str) -> str:
        """Generate cache key for permission check."""
        key_str = f"{subject_id}:{action}:{resource_type}:{resource_id}"
        return f"perm:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def invalidate_cache(self, subject_id: Optional[str] = None):
        """Invalidate permission cache."""
        if subject_id:
            # Invalidate specific subject
            pattern = f"perm:*{subject_id}*"
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
        else:
            # Invalidate all
            for key in self.redis.scan_iter(match="perm:*"):
                self.redis.delete(key)
