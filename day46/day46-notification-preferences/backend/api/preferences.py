from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from services.preference_service import PreferenceService
from pydantic import BaseModel
from datetime import time
from models.notification_preference import NotificationChannel, NotificationCategory, NotificationPriority

router = APIRouter()

class PreferenceCreateRequest(BaseModel):
    user_id: int
    global_quiet_hours_enabled: bool = False

class QuietHoursRequest(BaseModel):
    start_time: str  # "22:00"
    end_time: str    # "08:00"
    timezone: str = "UTC"
    days_of_week: List[int] = [0,1,2,3,4,5,6]
    exceptions: List[str] = ["security", "critical"]

class ChannelPreferenceRequest(BaseModel):
    channel: str
    priority_score: int
    is_enabled: bool = True

class EscalationRuleRequest(BaseModel):
    category: str
    priority_threshold: str = "high"
    escalation_delay_minutes: int = 15
    escalation_channels: List[str] = []
    escalation_contacts: List[str] = []
    max_attempts: int = 3

@router.post("/")
async def create_preference(request: PreferenceCreateRequest, db: Session = Depends(get_db)):
    service = PreferenceService(db)
    return service.create_user_preference(request.user_id, request.global_quiet_hours_enabled)

@router.get("/{user_id}")
async def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
    service = PreferenceService(db)
    preferences = service.get_user_preferences(user_id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preferences

@router.put("/{user_id}/quiet-hours")
async def update_quiet_hours(user_id: int, request: QuietHoursRequest, db: Session = Depends(get_db)):
    service = PreferenceService(db)
    return service.update_quiet_hours(user_id, request.dict())

@router.put("/{user_id}/channels")
async def update_channel_preferences(user_id: int, channels: List[ChannelPreferenceRequest], db: Session = Depends(get_db)):
    service = PreferenceService(db)
    return service.update_channel_preferences(user_id, [c.dict() for c in channels])

@router.post("/{user_id}/escalation-rules")
async def create_escalation_rule(user_id: int, request: EscalationRuleRequest, db: Session = Depends(get_db)):
    service = PreferenceService(db)
    return service.create_escalation_rule(user_id, request.dict())

@router.get("/{user_id}/escalation-rules")
async def get_escalation_rules(user_id: int, db: Session = Depends(get_db)):
    service = PreferenceService(db)
    return service.get_escalation_rules(user_id)

@router.post("/{user_id}/test-preferences")
async def test_notification_preferences(user_id: int, notification_data: dict, db: Session = Depends(get_db)):
    """Test how a notification would be processed given user preferences"""
    service = PreferenceService(db)
    return service.test_notification_processing(user_id, notification_data)
