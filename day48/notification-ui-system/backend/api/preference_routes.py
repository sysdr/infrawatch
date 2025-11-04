from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.service_container import notification_service
from models.notification import UpdatePreferenceRequest

router = APIRouter()

@router.get("/")
async def get_preferences(user_id: str = "demo-user"):
    """Get notification preferences for a user"""
    try:
        preferences = await notification_service.get_preferences(user_id)
        return {"preferences": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{preference_id}")
async def update_preference(
    preference_id: str,
    request: UpdatePreferenceRequest,
    user_id: str = "demo-user"
):
    """Update notification preference"""
    try:
        # Only include fields that were actually set (exclude None values)
        update_data = request.model_dump(exclude_none=True)
        
        # Validate that at least one field is being updated
        if not update_data:
            raise HTTPException(status_code=400, detail="At least one field must be provided for update")
        
        await notification_service.update_preference(
            user_id, preference_id, update_data
        )
        return {"status": "updated", "preferenceId": preference_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
