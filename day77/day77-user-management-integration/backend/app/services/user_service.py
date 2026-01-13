from sqlalchemy.orm import Session
from app.models import User, UserStatus, AuditLog
from app.schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext
from datetime import datetime
from app.core.redis_client import get_redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        hashed_password = pwd_context.hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            status=UserStatus.PENDING
        )
        db.add(user)
        db.flush()
        
        # Log audit
        audit = AuditLog(
            user_id=user.id,
            action="user_created",
            resource_type="user",
            resource_id=str(user.id),
            details={"email": user.email}
        )
        db.add(audit)
        db.commit()
        db.refresh(user)
        
        # Invalidate cache
        redis = get_redis()
        redis.delete(f"user:{user.id}")
        
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        # Log audit
        audit = AuditLog(
            user_id=user.id,
            action="user_updated",
            resource_type="user",
            resource_id=str(user.id),
            details=update_data
        )
        db.add(audit)
        db.commit()
        db.refresh(user)
        
        # Invalidate cache
        redis = get_redis()
        redis.delete(f"user:{user.id}")
        
        return user
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user.status = UserStatus.ACTIVE
        user.is_active = True
        user.updated_at = datetime.utcnow()
        
        # Log audit
        audit = AuditLog(
            user_id=user.id,
            action="user_activated",
            resource_type="user",
            resource_id=str(user.id)
        )
        db.add(audit)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def suspend_user(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user.status = UserStatus.SUSPENDED
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        # Log audit
        audit = AuditLog(
            user_id=user.id,
            action="user_suspended",
            resource_type="user",
            resource_id=str(user.id)
        )
        db.add(audit)
        db.commit()
        db.refresh(user)
        
        # Invalidate all user sessions
        redis = get_redis()
        redis.delete(f"sessions:user:{user.id}")
        
        return user
    
    @staticmethod
    def archive_user(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user.status = UserStatus.ARCHIVED
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        # Log audit
        audit = AuditLog(
            user_id=user.id,
            action="user_archived",
            resource_type="user",
            resource_id=str(user.id)
        )
        db.add(audit)
        db.commit()
        db.refresh(user)
        
        return user
