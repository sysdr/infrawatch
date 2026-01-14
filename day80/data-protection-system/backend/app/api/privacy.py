from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.services.privacy_service import privacy_service, CONSENT_PURPOSES
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import ConsentRecord, AuditLog
from datetime import datetime

router = APIRouter()

class ConsentRequest(BaseModel):
    user_id: int
    purposes: List[str]

class ConsentCheckRequest(BaseModel):
    user_id: int
    purpose: str

@router.post("/grant-consent")
async def grant_consent(request: ConsentRequest):
    """Grant consent for user"""
    try:
        bitfield = await privacy_service.grant_consent(request.user_id, request.purposes)
        return {
            "success": True,
            "user_id": request.user_id,
            "purposes": request.purposes,
            "bitfield": bitfield
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revoke-consent")
async def revoke_consent(request: ConsentRequest):
    """Revoke consent for user"""
    try:
        bitfield = await privacy_service.revoke_consent(request.user_id, request.purposes)
        return {
            "success": True,
            "user_id": request.user_id,
            "revoked_purposes": request.purposes,
            "bitfield": bitfield
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-consent")
async def check_consent(request: ConsentCheckRequest):
    """Check if user has granted consent for purpose"""
    try:
        has_consent = await privacy_service.check_consent(request.user_id, request.purpose)
        return {
            "user_id": request.user_id,
            "purpose": request.purpose,
            "granted": has_consent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-consents/{user_id}")
async def get_user_consents(user_id: int):
    """Get all consents for user"""
    try:
        consents = await privacy_service.get_user_consents(user_id)
        return {
            "user_id": user_id,
            "consents": consents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purposes")
async def get_consent_purposes():
    """Get all available consent purposes"""
    return {
        "purposes": list(CONSENT_PURPOSES.keys()),
        "total": len(CONSENT_PURPOSES)
    }

@router.post("/log-access")
async def log_data_access(
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: str,
    purpose: str,
    legal_basis: str,
    db: Session = Depends(get_db)
):
    """Log data access for audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            purpose=purpose,
            legal_basis=legal_basis,
            ip_address="127.0.0.1"
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "log_id": audit_log.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-logs/{user_id}")
async def get_audit_logs(user_id: int, limit: int = 100, db: Session = Depends(get_db)):
    """Get audit logs for user"""
    try:
        logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
        
        return {
            "user_id": user_id,
            "count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "resource": f"{log.resource_type}:{log.resource_id}",
                    "purpose": log.purpose,
                    "legal_basis": log.legal_basis,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
