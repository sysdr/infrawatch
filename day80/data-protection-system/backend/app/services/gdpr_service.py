from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import logging
from sqlalchemy.orm import Session
from app.models.user import User, AuditLog, GDPRRequest

logger = logging.getLogger(__name__)

class GDPRService:
    def __init__(self):
        self.export_batch_size = 1000
    
    async def create_access_request(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Create GDPR data access request"""
        request = GDPRRequest(
            user_id=user_id,
            request_type="access",
            status="pending"
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        
        logger.info(f"Created access request {request.id} for user {user_id}")
        return {
            "request_id": request.id,
            "status": "pending",
            "estimated_completion": datetime.now() + timedelta(days=30)
        }
    
    async def process_access_request(self, request_id: int, db: Session) -> Dict[str, Any]:
        """Process GDPR access request and generate export"""
        request = db.query(GDPRRequest).filter(GDPRRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        request.status = "processing"
        db.commit()
        
        try:
            # Collect all user data
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise ValueError(f"User {request.user_id} not found")
            
            # Gather data from all tables
            export_data = {
                "user_profile": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                },
                "audit_logs": [],
                "consents": {},
                "data_classification": user.classification.value if user.classification else None
            }
            
            # Get audit logs
            audit_logs = db.query(AuditLog).filter(
                AuditLog.user_id == request.user_id
            ).order_by(AuditLog.timestamp.desc()).limit(1000).all()
            
            export_data["audit_logs"] = [
                {
                    "action": log.action,
                    "resource": f"{log.resource_type}:{log.resource_id}",
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "purpose": log.purpose
                }
                for log in audit_logs
            ]
            
            # Generate export file
            export_json = json.dumps(export_data, indent=2)
            result_path = f"/tmp/gdpr_export_{request.user_id}_{request.id}.json"
            
            with open(result_path, 'w') as f:
                f.write(export_json)
            
            request.status = "completed"
            request.completed_at = datetime.now()
            request.result_location = result_path
            db.commit()
            
            logger.info(f"Completed access request {request_id}")
            return {
                "request_id": request.id,
                "status": "completed",
                "export_location": result_path,
                "record_count": len(export_data["audit_logs"])
            }
            
        except Exception as e:
            request.status = "failed"
            request.error_message = str(e)
            db.commit()
            logger.error(f"Failed to process access request {request_id}: {e}")
            raise
    
    async def create_erasure_request(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Create GDPR right to erasure (right to be forgotten) request"""
        request = GDPRRequest(
            user_id=user_id,
            request_type="erasure",
            status="pending"
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        
        logger.info(f"Created erasure request {request.id} for user {user_id}")
        return {
            "request_id": request.id,
            "status": "pending",
            "estimated_completion": datetime.now() + timedelta(days=30)
        }
    
    async def process_erasure_request(self, request_id: int, db: Session) -> Dict[str, Any]:
        """Process GDPR erasure request (soft delete with tombstone)"""
        request = db.query(GDPRRequest).filter(GDPRRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        request.status = "processing"
        db.commit()
        
        try:
            # Soft delete user
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise ValueError(f"User {request.user_id} not found")
            
            user.deleted_at = datetime.now()
            user.is_active = False
            user.email = f"deleted_{user.id}@deleted.com"
            user.full_name = "DELETED"
            user.phone = None
            
            # Clear encrypted data
            user.email_encrypted = None
            user.full_name_encrypted = None
            user.phone_encrypted = None
            user.ssn_encrypted = None
            user.credit_card_encrypted = None
            
            db.commit()
            
            request.status = "completed"
            request.completed_at = datetime.now()
            db.commit()
            
            logger.info(f"Completed erasure request {request_id}")
            return {
                "request_id": request.id,
                "status": "completed",
                "user_id": request.user_id,
                "erased_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            request.status = "failed"
            request.error_message = str(e)
            db.commit()
            logger.error(f"Failed to process erasure request {request_id}: {e}")
            raise
    
    async def create_portability_request(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Create GDPR data portability request"""
        # Similar to access request but in machine-readable format
        return await self.create_access_request(user_id, db)
    
    async def get_request_status(self, request_id: int, db: Session) -> Dict[str, Any]:
        """Get status of GDPR request"""
        request = db.query(GDPRRequest).filter(GDPRRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        return {
            "request_id": request.id,
            "user_id": request.user_id,
            "type": request.request_type,
            "status": request.status,
            "requested_at": request.requested_at.isoformat() if request.requested_at else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "result_location": request.result_location,
            "error_message": request.error_message
        }

# Global instance
gdpr_service = GDPRService()
