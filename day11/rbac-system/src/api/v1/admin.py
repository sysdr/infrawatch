from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database.config import get_db
from src.models.user import User, Role, Permission
from src.schemas.user import (
    User as UserSchema, UserCreate, UserUpdate,
    Role as RoleSchema, RoleCreate,
    Permission as PermissionSchema, PermissionCreate,
    RoleAssignment
)
from src.auth.rbac import get_current_user, require_permissions, invalidate_user_permissions_cache
from src.auth.utils import get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])

# User Management
@router.get("/users", response_model=List[UserSchema])
@require_permissions("manage_users")
async def list_users(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/users", response_model=UserSchema)
@require_permissions("manage_users")
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    # Assign roles if provided
    if user.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user.role_ids)).all()
        db_user.roles = roles
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/users/{user_id}", response_model=UserSchema)
@require_permissions("manage_users")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information (admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.username is not None:
        db_user.username = user_update.username
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    
    # Update roles if provided
    if user_update.role_ids is not None:
        roles = db.query(Role).filter(Role.id.in_(user_update.role_ids)).all()
        db_user.roles = roles
        # Invalidate user's permission cache
        invalidate_user_permissions_cache(user_id)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Role Management
@router.get("/roles", response_model=List[RoleSchema])
@require_permissions("manage_roles")
async def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all roles (admin only)"""
    roles = db.query(Role).all()
    return roles

@router.post("/roles", response_model=RoleSchema)
@require_permissions("manage_roles")
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new role (admin only)"""
    # Check if role already exists
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    # Create new role
    db_role = Role(name=role.name, description=role.description)
    
    # Assign permissions if provided
    if role.permission_ids:
        permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
        db_role.permissions = permissions
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    
    return db_role

# Permission Management
@router.get("/permissions", response_model=List[PermissionSchema])
@require_permissions("manage_permissions")
async def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all permissions (admin only)"""
    permissions = db.query(Permission).all()
    return permissions

@router.post("/permissions", response_model=PermissionSchema)
@require_permissions("manage_permissions")
async def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new permission (admin only)"""
    # Check if permission already exists
    existing_permission = db.query(Permission).filter(Permission.name == permission.name).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )
    
    db_permission = Permission(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    
    return db_permission

# Role Assignment
@router.post("/assign-roles")
@require_permissions("manage_users")
async def assign_roles(
    assignment: RoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign roles to a user (admin only)"""
    user = db.query(User).filter(User.id == assignment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    roles = db.query(Role).filter(Role.id.in_(assignment.role_ids)).all()
    user.roles = roles
    
    # Invalidate user's permission cache
    invalidate_user_permissions_cache(assignment.user_id)
    
    db.commit()
    
    return {"message": "Roles assigned successfully"}
