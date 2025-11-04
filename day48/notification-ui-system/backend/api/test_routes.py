from fastapi import APIRouter, HTTPException
from services.service_container import notification_service

router = APIRouter()

@router.post("/notification")
async def generate_test_notification(
    test_type: str = "info",
    user_id: str = "demo-user"
):
    """Generate test notification"""
    try:
        notification = await notification_service.generate_test_notification(user_id, test_type)
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_test_types():
    """Get available test notification types"""
    return {
        "types": ["success", "error", "warning", "info"],
        "description": "Available test notification types"
    }
