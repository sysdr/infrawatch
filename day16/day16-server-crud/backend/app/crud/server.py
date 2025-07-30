from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from app.models.server import Server
from app.schemas.server import ServerCreate, ServerUpdate
from datetime import datetime

class ServerCRUD:
    def create(self, db: Session, obj_in: ServerCreate, user_id: str) -> Server:
        db_obj = Server(**obj_in.dict())
        db.add(db_obj)
        db.flush()
        
        # Log audit trail
        from app.crud.audit import audit_crud
        audit_crud.log_action(
            db=db,
            resource_type="server",
            resource_id=str(db_obj.id),
            action="create",
            user_id=user_id,
            tenant_id=obj_in.tenant_id,
            changes=obj_in.dict()
        )
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int, tenant_id: str) -> Optional[Server]:
        return db.query(Server).filter(
            and_(
                Server.id == id,
                Server.tenant_id == tenant_id,
                Server.is_deleted == False
            )
        ).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        region: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        query = db.query(Server).filter(
            and_(
                Server.tenant_id == tenant_id,
                Server.is_deleted == False
            )
        )
        
        # Apply filters
        if status:
            query = query.filter(Server.status == status)
        if environment:
            query = query.filter(Server.environment == environment)
        if region:
            query = query.filter(Server.region == region)
        if search:
            query = query.filter(
                or_(
                    Server.name.ilike(f"%{search}%"),
                    Server.hostname.ilike(f"%{search}%"),
                    Server.ip_address.ilike(f"%{search}%")
                )
            )
        
        total = query.count()
        servers = query.offset(skip).limit(limit).all()
        
        return {
            "servers": servers,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    def update(
        self,
        db: Session,
        db_obj: Server,
        obj_in: ServerUpdate,
        user_id: str
    ) -> Server:
        old_data = {
            "name": db_obj.name,
            "hostname": db_obj.hostname,
            "ip_address": db_obj.ip_address,
            "status": db_obj.status,
            "version": db_obj.version
        }
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db_obj.version += 1
        db_obj.updated_at = datetime.utcnow()
        
        # Log audit trail
        from app.crud.audit import audit_crud
        audit_crud.log_action(
            db=db,
            resource_type="server",
            resource_id=str(db_obj.id),
            action="update",
            user_id=user_id,
            tenant_id=db_obj.tenant_id,
            changes={"old": old_data, "new": update_data}
        )
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def soft_delete(self, db: Session, db_obj: Server, user_id: str) -> Server:
        db_obj.is_deleted = True
        db_obj.deleted_at = datetime.utcnow()
        db_obj.status = "decommissioned"
        
        # Log audit trail
        from app.crud.audit import audit_crud
        audit_crud.log_action(
            db=db,
            resource_type="server",
            resource_id=str(db_obj.id),
            action="delete",
            user_id=user_id,
            tenant_id=db_obj.tenant_id,
            changes={"deleted_at": db_obj.deleted_at.isoformat()}
        )
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

server_crud = ServerCRUD()
