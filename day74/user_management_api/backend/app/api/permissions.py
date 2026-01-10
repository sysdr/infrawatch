from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from uuid import UUID

from app.core.database import get_db
from app.models.permission import Permission, UserPermission
from app.models.user import User
from app.schemas.permission import (
    PermissionCreate, PermissionResponse,
    PermissionAssign, PermissionCheckRequest, PermissionCheckResponse
)
from app.services.permission_service import PermissionService
from app.services.cache_service import CacheService

router = APIRouter()

def get_permission_service(request: Request, db: AsyncSession = Depends(get_db)):
    cache = CacheService(request.app.state.redis)
    return PermissionService(db, cache)

@router.get("", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db)
):
    """List all permissions"""
    result = await db.execute(select(Permission))
    permissions = result.scalars().all()
    return permissions

@router.post("", response_model=PermissionResponse, status_code=201)
async def create_permission(
    perm_data: PermissionCreate,
    db: AsyncSession = Depends(get_db)
):
    permission = Permission(**perm_data.dict())
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission

@router.post("/users/{user_id}/assign", status_code=201)
async def assign_permission_to_user(
    user_id: UUID,
    perm_data: PermissionAssign,
    db: AsyncSession = Depends(get_db),
    perm_service: PermissionService = Depends(get_permission_service)
):
    # Check if already assigned
    result = await db.execute(
        select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == perm_data.permission_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Permission already assigned")
    
    user_perm = UserPermission(
        user_id=user_id,
        permission_id=perm_data.permission_id
    )
    db.add(user_perm)
    await db.commit()
    
    # Invalidate cache
    await perm_service.invalidate_user_cache(user_id)
    
    return {"message": "Permission assigned"}

@router.post("/users/{user_id}/check", response_model=PermissionCheckResponse)
async def check_user_permission(
    user_id: UUID,
    check_data: PermissionCheckRequest,
    perm_service: PermissionService = Depends(get_permission_service),
    db: AsyncSession = Depends(get_db)
):
    # Normalize resource and action
    resource = check_data.resource.lower().strip()
    action = check_data.action.lower().strip()
    
    # Check if user exists (basic validation)
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        return PermissionCheckResponse(
            allowed=False,
            reason=f"User with ID {user_id} not found"
        )
    
    # Check permission using the service
    allowed = await perm_service.check_permission(user_id, resource, action)
    
    # Get user's permissions for better error message
    user_perms = await perm_service.get_user_permissions(user_id)
    
    if allowed:
        reason = f"Permission granted: User has {resource}:{action} permission"
    else:
        if not user_perms:
            reason = "Permission denied: User has no permissions assigned. Please assign permissions to this user first using the 'Assign Permission' tab."
        else:
            # Check what permissions the user actually has for this resource
            user_resource_perms = await db.execute(
                select(Permission.action)
                .join(UserPermission)
                .where(
                    UserPermission.user_id == user_id,
                    Permission.resource.ilike(f"%{resource}%")
                )
            )
            resource_actions = [perm.lower() for perm in user_resource_perms.scalars().all()]
            
            if resource_actions:
                reason = f"Permission denied: User has permissions for '{resource}' with actions: {', '.join(resource_actions)}, but not for action '{action}'. Please assign the correct permission or check the action."
            else:
                perm_list = ', '.join(list(user_perms)[:5])
                reason = f"Permission denied: User does not have any permissions for resource '{resource}'. User currently has permissions: {perm_list}. Please assign a permission with resource '{resource}' and action '{action}'."
    
    return PermissionCheckResponse(
        allowed=allowed,
        reason=reason
    )


@router.get("/users/{user_id}")
async def get_user_permissions(
    user_id: UUID,
    perm_service: PermissionService = Depends(get_permission_service)
):
    permissions = await perm_service.get_user_permissions(user_id)
    return {"permissions": list(permissions)}
