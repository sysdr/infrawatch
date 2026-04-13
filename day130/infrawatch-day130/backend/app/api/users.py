from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("", response_model=UserOut)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(User).where(User.username == data.username))).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(id=str(uuid.uuid4()), **data.model_dump())
    db.add(user); await db.commit(); await db.refresh(user)
    return user

@router.get("", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(User))).scalars().all()

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
