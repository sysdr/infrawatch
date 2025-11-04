from fastapi import APIRouter, HTTPException
from typing import Optional
from services.service_container import notification_service

router = APIRouter()

@router.get("/")
async def get_history(
    user_id: str = "demo-user",
    notification_id: Optional[str] = None
):
    """Get notification history"""
    try:
        history = await notification_service.get_history(user_id, notification_id)
        return {"history": history, "total": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
