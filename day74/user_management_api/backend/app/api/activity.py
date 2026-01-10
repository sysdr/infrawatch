from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityListResponse

router = APIRouter()

@router.post("/users/{user_id}", response_model=ActivityResponse, status_code=201)
async def create_activity(
    user_id: UUID,
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_db)
):
    activity = Activity(user_id=user_id, **activity_data.dict())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity

@router.get("/users/{user_id}", response_model=ActivityListResponse)
async def get_user_activities(
    user_id: UUID,
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    action: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Activity).where(Activity.user_id == user_id)
    
    if start_date:
        query = query.where(Activity.timestamp >= start_date)
    if end_date:
        query = query.where(Activity.timestamp <= end_date)
    if action:
        query = query.where(Activity.action == action)
    
    # Get total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get activities
    query = query.order_by(desc(Activity.timestamp))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    activities = result.scalars().all()
    
    return ActivityListResponse(activities=activities, total=total)

@router.get("/recent", response_model=ActivityListResponse)
async def get_recent_activities(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(Activity).where(Activity.timestamp >= since)
    query = query.order_by(desc(Activity.timestamp)).limit(limit)
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    return ActivityListResponse(activities=activities, total=len(activities))
