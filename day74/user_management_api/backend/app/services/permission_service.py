from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Set
from uuid import UUID

from app.models.permission import Permission, UserPermission, TeamPermission
from app.models.team import TeamMember
from app.services.cache_service import CacheService

class PermissionService:
    def __init__(self, db: AsyncSession, cache: CacheService):
        self.db = db
        self.cache = cache
    
    async def get_user_permissions(self, user_id: UUID) -> Set[str]:
        # Check cache first
        cache_key = f"user:{user_id}:permissions"
        cached = await self.cache.get(cache_key)
        if cached:
            return set(cached)
        
        # Get direct permissions - return permission names for display
        direct_perms = await self.db.execute(
            select(Permission.name)
            .join(UserPermission)
            .where(UserPermission.user_id == user_id)
        )
        permissions = set(direct_perms.scalars().all())
        
        # Get team permissions
        team_perms = await self.db.execute(
            select(Permission.name)
            .join(TeamPermission)
            .join(TeamMember, TeamMember.team_id == TeamPermission.team_id)
            .where(TeamMember.user_id == user_id)
        )
        permissions.update(team_perms.scalars().all())
        
        # Cache result
        await self.cache.set(cache_key, list(permissions))
        
        return permissions
    
    async def check_permission(self, user_id: UUID, resource: str, action: str) -> bool:
        """
        Check if user has permission for given resource and action.
        Checks both direct user permissions and team permissions.
        Supports wildcard action (*) which matches any action.
        """
        # Normalize inputs
        resource = resource.lower().strip()
        action = action.lower().strip()
        
        # Get all permissions the user has (via direct assignment or team membership)
        # We need to check Permission.resource and Permission.action fields, not just name
        direct_perms_query = (
            select(Permission.resource, Permission.action)
            .join(UserPermission)
            .where(UserPermission.user_id == user_id)
        )
        direct_perms = await self.db.execute(direct_perms_query)
        user_permissions = set((perm.resource.lower(), perm.action.lower()) for perm in direct_perms.all())
        
        # Get team permissions
        team_perms_query = (
            select(Permission.resource, Permission.action)
            .join(TeamPermission)
            .join(TeamMember, TeamMember.team_id == TeamPermission.team_id)
            .where(TeamMember.user_id == user_id)
        )
        team_perms = await self.db.execute(team_perms_query)
        user_permissions.update((perm.resource.lower(), perm.action.lower()) for perm in team_perms.all())
        
        # Check for exact match: resource:action
        if (resource, action) in user_permissions:
            return True
        
        # Check for wildcard action: resource:*
        if (resource, "*") in user_permissions or (resource, "all") in user_permissions:
            return True
        
        # Check if action is "*" and user has any permission for the resource
        if action == "*" or action == "all":
            if any(perm_resource == resource for perm_resource, _ in user_permissions):
                return True
        
        return False
    
    async def invalidate_user_cache(self, user_id: UUID):
        await self.cache.delete(f"user:{user_id}:permissions")
