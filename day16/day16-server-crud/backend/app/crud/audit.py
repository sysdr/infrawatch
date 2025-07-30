from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.audit import AuditLog
from datetime import datetime

class AuditCRUD:
    def log_action(
        self,
        db: Session,
        resource_type: str,
        resource_id: str,
        action: str,
        user_id: str,
        tenant_id: str,
        changes: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        audit_log = AuditLog(
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            user_id=user_id,
            tenant_id=tenant_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.flush()
        return audit_log
    
    def get_logs(
        self,
        db: Session,
        tenant_id: str,
        resource_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        
        return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

audit_crud = AuditCRUD()
