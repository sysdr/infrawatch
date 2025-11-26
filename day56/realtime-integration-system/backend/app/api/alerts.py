from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AlertRequest(BaseModel):
    severity: str
    message: str
    source: str = "system"

@router.post("/create")
async def create_alert(request: AlertRequest):
    """Create a new alert"""
    from app.main import integration_hub
    
    if not integration_hub:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    alert = await integration_hub.alert_dispatcher.dispatch_alert({
        "severity": request.severity,
        "message": request.message,
        "source": request.source
    })
    
    return alert
