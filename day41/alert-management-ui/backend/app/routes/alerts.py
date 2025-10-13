from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Import shared sample data
from data import sample_alerts

@router.get("/")
async def get_alerts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Get paginated alerts with filtering"""
    filtered_alerts = sample_alerts.copy()
    
    # Apply filters
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]
    if status:
        filtered_alerts = [a for a in filtered_alerts if a["status"] == status]
    if search:
        filtered_alerts = [a for a in filtered_alerts 
                         if search.lower() in a["title"].lower() or 
                            search.lower() in a["description"].lower()]
    
    # Pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_alerts = filtered_alerts[start_idx:end_idx]
    
    return {
        "alerts": paginated_alerts,
        "total": len(filtered_alerts),
        "page": page,
        "limit": limit,
        "pages": (len(filtered_alerts) + limit - 1) // limit
    }

@router.get("/stats/summary")
async def get_alert_stats():
    """Get alert statistics summary"""
    stats = {
        "total": len(sample_alerts),
        "critical": len([a for a in sample_alerts if a["severity"] == "critical"]),
        "warning": len([a for a in sample_alerts if a["severity"] == "warning"]),
        "info": len([a for a in sample_alerts if a["severity"] == "info"]),
        "active": len([a for a in sample_alerts if a["status"] == "active"]),
        "acknowledged": len([a for a in sample_alerts if a["status"] == "acknowledged"]),
        "resolved": len([a for a in sample_alerts if a["status"] == "resolved"])
    }
    return stats

# Bulk operations - must come before parameterized routes
@router.post("/bulk/acknowledge")
async def bulk_acknowledge(alert_ids: List[str]):
    """Bulk acknowledge alerts"""
    acknowledged = 0
    for alert_id in alert_ids:
        alert = next((a for a in sample_alerts if a["id"] == alert_id), None)
        if alert:
            if alert["status"] == "active":
                alert["status"] = "acknowledged"
                acknowledged += 1
    
    return {"message": f"Acknowledged {acknowledged} alerts"}

@router.post("/bulk/resolve")
async def bulk_resolve(alert_ids: List[str]):
    """Bulk resolve alerts"""
    resolved = 0
    for alert_id in alert_ids:
        alert = next((a for a in sample_alerts if a["id"] == alert_id), None)
        if alert:
            if alert["status"] in ["active", "acknowledged"]:
                alert["status"] = "resolved"
                resolved += 1
    
    return {"message": f"Resolved {resolved} alerts"}

# Individual alert operations - parameterized routes come last
@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """Get specific alert by ID"""
    alert = next((a for a in sample_alerts if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    alert = next((a for a in sample_alerts if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert["status"] = "acknowledged"
    alert["history"].append({
        "action": "acknowledged",
        "timestamp": datetime.now().isoformat(),
        "user": "current_user",
        "note": "Alert acknowledged via UI"
    })
    
    return {"message": "Alert acknowledged successfully"}

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    alert = next((a for a in sample_alerts if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert["status"] = "resolved"
    alert["history"].append({
        "action": "resolved",
        "timestamp": datetime.now().isoformat(),
        "user": "current_user", 
        "note": "Alert resolved via UI"
    })
    
    return {"message": "Alert resolved successfully"}

@router.post("/{alert_id}/assign")
async def assign_alert(alert_id: str, assignee: str):
    """Assign alert to user"""
    alert = next((a for a in sample_alerts if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert["assignee"] = assignee
    alert["history"].append({
        "action": "assigned",
        "timestamp": datetime.now().isoformat(),
        "user": "current_user",
        "note": f"Alert assigned to {assignee}"
    })
    
    return {"message": f"Alert assigned to {assignee}"}