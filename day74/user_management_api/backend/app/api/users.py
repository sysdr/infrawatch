from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from uuid import UUID
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.user import User, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.cache_service import CacheService

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_cache(request: Request) -> CacheService:
    return CacheService(request.app.state.redis)

@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    # Check if user exists
    result = await db.execute(
        select(User).where(
            or_(User.email == user_data.email, User.username == user_data.username)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    hashed_password = pwd_context.hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        status=UserStatus.INVITED
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Cache user
    cache_key = f"user:{user.id}"
    await cache.set(cache_key, {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "status": user.status.value
    })
    
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    # Check cache
    cache_key = f"user:{user_id}"
    cached = await cache.get(cache_key)
    if cached:
        return UserResponse(**cached)
    
    # Query database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cache result
    await cache.set(cache_key, {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "status": user.status.value,
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "last_login": user.last_login,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    })
    
    return user

@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[UserStatus] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    # Build query
    query = select(User)
    
    if status:
        query = query.where(User.status == status)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size
    )

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.status is not None:
        user.status = user_data.status
    
    await db.commit()
    await db.refresh(user)
    
    # Invalidate cache
    await cache.delete(f"user:{user_id}")
    
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete
    user.status = UserStatus.DELETED
    user.is_active = False
    
    await db.commit()
    
    # Invalidate cache
    await cache.delete(f"user:{user_id}")
    await cache.delete(f"user:{user_id}:permissions")
    
    return None
