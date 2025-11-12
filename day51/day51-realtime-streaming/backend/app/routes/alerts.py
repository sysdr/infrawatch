from fastapi import APIRouter
from typing import Dict, List

router = APIRouter()

@router.get("/history")
async def get_alert_history() -> List[Dict]:
    """Get alert history"""
    from app.main import alert_service
    return alert_service.alert_history[-50:]  # Last 50 alerts

@router.get("/stats")
async def get_alert_stats() -> Dict:
    """Get alert statistics"""
    from app.main import alert_service
    return alert_service.get_stats()

@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str) -> Dict:
    """Acknowledge an alert"""
    return {"status": "acknowledged", "alert_id": alert_id}
