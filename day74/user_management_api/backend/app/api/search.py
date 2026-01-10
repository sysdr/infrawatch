from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import Optional

from app.core.database import get_db
from app.models.user import User, UserStatus
from app.schemas.user import UserListResponse

router = APIRouter()

@router.get("/users", response_model=UserListResponse)
async def search_users(
    q: str = Query(..., min_length=1),
    status: Optional[UserStatus] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    # Build search query
    search_term = f"%{q}%"
    query = select(User).where(
        or_(
            User.email.ilike(search_term),
            User.username.ilike(search_term),
            User.full_name.ilike(search_term)
        )
    )
    
    if status:
        query = query.where(User.status == status)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Get total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get results
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size
    )
