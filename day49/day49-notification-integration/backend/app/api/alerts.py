from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import Alert, AlertStatus, AlertSeverity
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Notification service import removed to avoid connection issues
# Will be re-enabled once Redis/Database connection issues are resolved

router = APIRouter()

class AlertCreate(BaseModel):
    service_name: str
    alert_type: str
    severity: AlertSeverity
    message: str
    metadata: dict = {}

class AlertAck(BaseModel):
    user_id: str

@router.post("/")
async def create_alert(alert_data: AlertCreate, db: AsyncSession = Depends(get_db)):
    """Create new alert and trigger notifications"""
    try:
        alert = Alert(
            service_name=alert_data.service_name,
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            message=alert_data.message,
            alert_metadata=alert_data.metadata
        )
        db.add(alert)
        await db.flush()
        alert_id = alert.id
        await db.commit()
        
        return {"id": alert_id, "status": "NEW", "message": "Alert created"}
    except Exception as e:
        logger.error(f"Error creating alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.get("/")
async def list_alerts(
    status: Optional[AlertStatus] = None,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """List alerts with optional status filter and limit"""
    try:
        query = select(Alert).order_by(Alert.created_at.desc())
        if status:
            query = query.where(Alert.status == status)
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        return [
            {
                "id": a.id,
                "service_name": a.service_name,
                "severity": a.severity.value if hasattr(a.severity, 'value') else str(a.severity),
                "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
                "message": a.message,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "acknowledged_by": a.acknowledged_by,
                "escalation_level": a.escalation_level
            }
            for a in alerts
        ]
    except Exception as e:
        logger.error(f"Error listing alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list alerts: {str(e)}")

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, ack: AlertAck, db: AsyncSession = Depends(get_db)):
    """Acknowledge alert"""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = ack.user_id
        alert.acknowledged_at = datetime.utcnow()
        await db.commit()
        
        return {"message": "Alert acknowledged"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Resolve alert"""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        await db.commit()
        
        return {"message": "Alert resolved"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")
