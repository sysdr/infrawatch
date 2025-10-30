from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from services.user_service import UserService
from pydantic import BaseModel

router = APIRouter()

class UserCreateRequest(BaseModel):
    username: str
    email: str
    phone: str = None
    timezone: str = "UTC"

@router.post("/")
async def create_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(request.dict())

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/")
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.list_users(skip, limit)
