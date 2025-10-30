from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from services.notification_service import NotificationService
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class NotificationRequest(BaseModel):
    user_id: int
    category: str
    priority: str
    title: str
    message: str
    data: Dict[str, Any] = {}

@router.post("/send")
async def send_notification(request: NotificationRequest, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.process_notification(request.dict())

@router.post("/simulate")
async def simulate_notification(request: NotificationRequest, db: Session = Depends(get_db)):
    """Simulate notification processing without actually sending"""
    service = NotificationService(db)
    return service.simulate_notification_processing(request.dict())
