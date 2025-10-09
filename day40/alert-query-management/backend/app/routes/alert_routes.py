from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from ..models.database import get_db
from ..services.alert_service import AlertQueryService
from ..models.alert_models import Alert, AlertStatus, AlertSeverity
from pydantic import BaseModel, field_validator

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

class AlertSearchRequest(BaseModel):
    query: Optional[str] = None
    status: Optional[List[str]] = None
    severity: Optional[List[str]] = None
    source: Optional[List[str]] = None
    service: Optional[List[str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 100
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"
    

class BulkUpdateRequest(BaseModel):
    alert_ids: List[int]
    updates: Dict[str, Any]

@router.post("/search")
async def search_alerts(
    request: AlertSearchRequest,
    db: Session = Depends(get_db)
):
    """Search alerts with advanced filtering"""
    service = AlertQueryService(db)
    
    try:
        # Convert string datetime to datetime object if needed
        start_time = None
        end_time = None
        
        if request.start_time and request.start_time.strip():
            try:
                start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
            except ValueError:
                pass
                
        if request.end_time and request.end_time.strip():
            try:
                end_time = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        result = service.search_alerts(
            query=request.query,
            status=request.status,
            severity=request.severity,
            source=request.source,
            service=request.service,
            start_time=start_time,
            end_time=end_time,
            tags=request.tags,
            limit=request.limit,
            offset=request.offset,
            sort_by=request.sort_by,
            sort_order=request.sort_order
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_alert_statistics(db: Session = Depends(get_db)):
    """Get alert statistics and metrics"""
    service = AlertQueryService(db)
    
    try:
        stats = service.get_alert_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-update")
async def bulk_update_alerts(
    request: BulkUpdateRequest,
    db: Session = Depends(get_db)
):
    """Bulk update multiple alerts"""
    service = AlertQueryService(db)
    
    try:
        result = service.bulk_update_alerts(request.alert_ids, request.updates)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_alerts(
    alert_ids: List[int],
    format: str = Query(default="csv", regex="^(csv|json)$"),
    db: Session = Depends(get_db)
):
    """Export alerts to various formats"""
    service = AlertQueryService(db)
    
    try:
        result = service.export_alerts(alert_ids, format)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return Response(
            content=result["data"],
            media_type=result["content_type"],
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters")
async def get_filter_options(db: Session = Depends(get_db)):
    """Get available filter options"""
    try:
        # Get unique values for filters
        sources = db.query(Alert.source).distinct().all()
        services = db.query(Alert.service).distinct().all()
        
        return {
            "statuses": [status.value for status in AlertStatus],
            "severities": [severity.value for severity in AlertSeverity],
            "sources": [s.source for s in sources if s.source],
            "services": [s.service for s in services if s.service]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
