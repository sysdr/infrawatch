from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from app.services.gdpr_service import gdpr_service
from sqlalchemy.orm import Session
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class GDPRRequest(BaseModel):
    user_id: int

@router.post("/access-request")
async def create_access_request(
    request: GDPRRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create GDPR data access request"""
    try:
        result = await gdpr_service.create_access_request(request.user_id, db)
        
        # Process request in background
        background_tasks.add_task(
            gdpr_service.process_access_request,
            result["request_id"],
            db
        )
        
        return result
    except Exception as e:
        logger.error(f"Access request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/erasure-request")
async def create_erasure_request(
    request: GDPRRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create GDPR erasure request (right to be forgotten)"""
    try:
        result = await gdpr_service.create_erasure_request(request.user_id, db)
        
        # Process request in background
        background_tasks.add_task(
            gdpr_service.process_erasure_request,
            result["request_id"],
            db
        )
        
        return result
    except Exception as e:
        logger.error(f"Erasure request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portability-request")
async def create_portability_request(
    request: GDPRRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create GDPR data portability request"""
    try:
        result = await gdpr_service.create_portability_request(request.user_id, db)
        
        # Process request in background
        background_tasks.add_task(
            gdpr_service.process_access_request,
            result["request_id"],
            db
        )
        
        return result
    except Exception as e:
        logger.error(f"Portability request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/request-status/{request_id}")
async def get_request_status(request_id: int, db: Session = Depends(get_db)):
    """Get GDPR request status"""
    try:
        status = await gdpr_service.get_request_status(request_id, db)
        return status
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/process-request/{request_id}")
async def process_request_manually(request_id: int, db: Session = Depends(get_db)):
    """Manually trigger processing of GDPR request"""
    try:
        from app.models.user import GDPRRequest as GDPRRequestModel
        
        request = db.query(GDPRRequestModel).filter(GDPRRequestModel.id == request_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if request.request_type == "access" or request.request_type == "portability":
            result = await gdpr_service.process_access_request(request_id, db)
        elif request.request_type == "erasure":
            result = await gdpr_service.process_erasure_request(request_id, db)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown request type: {request.request_type}")
        
        return result
    except Exception as e:
        logger.error(f"Manual processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
