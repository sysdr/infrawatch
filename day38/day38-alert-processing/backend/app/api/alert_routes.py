from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text, select, func
from ..services.alert_processor import AlertProcessor
from ..models.database import get_db_session
from ..models.alert import Alert, AlertState, AlertSeverity
from pydantic import BaseModel

router = APIRouter()

# This will be injected from main.py
def get_alert_processor() -> AlertProcessor:
    from ..main import alert_processor
    return alert_processor

class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    metric_name: str
    service_name: str
    current_value: float
    threshold_value: float

class AlertAcknowledge(BaseModel):
    acknowledged_by: str

class AlertResolve(BaseModel):
    resolved_by: str

@router.post("/alerts", response_model=Dict[str, Any])
async def create_alert(alert_data: AlertCreate, processor: AlertProcessor = Depends(get_alert_processor)):
    """Create new alert"""
    try:
        alert = await processor.process_alert(alert_data.dict())
        return {"status": "success", "alert": alert.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_alerts(
    state: Optional[AlertState] = None,
    severity: Optional[AlertSeverity] = None,
    service: Optional[str] = None,
    limit: int = 100
):
    """Get alerts with optional filtering"""
    async with get_db_session() as session:
        # Use SQLAlchemy 2.0 async syntax
        query = select(Alert)
        
        if state:
            query = query.where(Alert.state == state)
        if severity:
            query = query.where(Alert.severity == severity)
        if service:
            query = query.where(Alert.service_name == service)
        
        query = query.order_by(Alert.created_at.desc()).limit(limit)
        
        result = await session.execute(query)
        alert_objects = result.scalars().all()
        
        # Convert to dicts
        alert_dicts = [alert.to_dict() for alert in alert_objects]
        
        return alert_dicts

@router.get("/alerts/{alert_id}", response_model=Dict[str, Any])
async def get_alert(alert_id: str):
    """Get specific alert"""
    async with get_db_session() as session:
        alert = await session.get(Alert, alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert.to_dict()

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, ack_data: AlertAcknowledge, processor: AlertProcessor = Depends(get_alert_processor)):
    """Acknowledge an alert"""
    try:
        alert = await processor.acknowledge_alert(alert_id, ack_data.acknowledged_by)
        return {"status": "success", "alert": alert.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolve_data: AlertResolve, processor: AlertProcessor = Depends(get_alert_processor)):
    """Resolve an alert"""
    try:
        alert = await processor.resolve_alert(alert_id, resolve_data.resolved_by)
        return {"status": "success", "alert": alert.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/stats/summary")
async def get_alert_stats():
    """Get alert statistics"""
    async with get_db_session() as session:
        # Get counts by state using SQLAlchemy 2.0 async syntax
        state_counts = {}
        for state in AlertState:
            result = await session.execute(
                select(func.count(Alert.id)).where(Alert.state == state)
            )
            state_counts[state.value] = result.scalar()
        
        # Get counts by severity using SQLAlchemy 2.0 async syntax
        severity_counts = {}
        for severity in AlertSeverity:
            result = await session.execute(
                select(func.count(Alert.id)).where(
                    Alert.severity == severity,
                    Alert.state != AlertState.RESOLVED
                )
            )
            severity_counts[severity.value] = result.scalar()
        
        # Get recent activity using SQLAlchemy 2.0 async syntax
        last_24h = datetime.utcnow() - timedelta(hours=24)
        result = await session.execute(
            select(func.count(Alert.id)).where(Alert.created_at > last_24h)
        )
        recent_count = result.scalar()
        
        return {
            "states": state_counts,
            "severities": severity_counts,
            "recent_24h": recent_count,
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/alerts/history/{alert_id}")
async def get_alert_history(alert_id: str):
    """Get alert history and lifecycle events"""
    async with get_db_session() as session:
        alert = await session.get(Alert, alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # In real implementation, would query separate audit table
        history = [
            {
                "event": "created",
                "timestamp": alert.created_at.isoformat(),
                "details": f"Alert created with severity {alert.severity.value}"
            }
        ]
        
        if alert.acknowledged_at:
            history.append({
                "event": "acknowledged",
                "timestamp": alert.acknowledged_at.isoformat(),
                "user": alert.acknowledged_by,
                "details": f"Alert acknowledged by {alert.acknowledged_by}"
            })
        
        if alert.resolved_at:
            history.append({
                "event": "resolved",
                "timestamp": alert.resolved_at.isoformat(),
                "user": alert.resolved_by,
                "details": f"Alert resolved by {alert.resolved_by}" + 
                         (" (auto-resolved)" if alert.auto_resolved else "")
            })
        
        return {
            "alert_id": alert_id,
            "history": history
        }
