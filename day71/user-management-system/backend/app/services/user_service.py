from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional
from datetime import datetime, timedelta
import logging
from ..models.user import User, UserStatus
from ..models.profile import UserProfile
from ..models.preference import UserPreference, DEFAULT_PREFERENCES
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password
from ..core.redis_client import redis_client
from .activity_service import activity_service

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def create_user(db: Session, user_data: UserCreate) -> User:
        try:
            user = User(
                email=user_data.email,
                username=user_data.username or user_data.email.split('@')[0],
                hashed_password=get_password_hash(user_data.password)
            )
            db.add(user)
            db.flush()
            
            # Create profile
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            
            # Create preferences
            preferences = UserPreference(
                user_id=user.id,
                preferences=DEFAULT_PREFERENCES
            )
            db.add(preferences)
            
            db.commit()
            db.refresh(user)
            
            # Track activity (non-blocking - don't fail registration if this fails)
            try:
            await activity_service.track_activity(
                db, user.id, "user.created",
                description="User account created"
            )
            except Exception as e:
                logger.warning(f"Failed to track user creation activity: {e}")
            
            return user
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Integrity error during user creation: {e}")
            raise ValueError("Email or username already exists")
        except SQLAlchemyError as e:
            db.rollback()
            error_msg = str(e)
            logger.error(f"Database error during user creation: {e}", exc_info=True)
            
            # Provide more specific error messages
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                raise ValueError("Cannot connect to database. Please ensure PostgreSQL is running.")
            elif "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                raise ValueError("Email or username already exists")
            else:
                raise ValueError(f"Database error: {error_msg}")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error during user creation: {e}", exc_info=True)
            raise ValueError("An error occurred during registration. Please try again.")
    
    @staticmethod
    async def authenticate_user(
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        # Check if locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise ValueError("Account is temporarily locked")
        
        if not verify_password(password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
            
            await activity_service.track_activity(
                db, user.id, "auth.failed",
                description="Failed login attempt",
                ip_address=ip_address
            )
            return None
        
        # Successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        if user.status == UserStatus.PENDING:
            user.status = UserStatus.ACTIVE
        db.commit()
        
        await activity_service.track_activity(
            db, user.id, "auth.login",
            description="User logged in",
            ip_address=ip_address
        )
        
        return user
    
    @staticmethod
    async def get_user_with_cache(db: Session, user_id: int) -> Optional[User]:
        # Try cache first
        cached = await redis_client.get(f"user:{user_id}")
        if cached:
            # Note: In production, you'd reconstruct the User object
            # For simplicity, we'll query DB
            pass
        
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Cache user data (simplified)
            await redis_client.set(
                f"user:{user_id}",
                {"id": user.id, "email": user.email},
                expire=1800
            )
        return user
    
    @staticmethod
    async def update_user(
        db: Session,
        user_id: int,
        user_data: UserUpdate
    ) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        update_dict = user_data.dict(exclude_unset=True)
        if 'password' in update_dict:
            update_dict['hashed_password'] = get_password_hash(update_dict.pop('password'))
        
        for key, value in update_dict.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Invalidate cache
        await redis_client.delete(f"user:{user_id}")
        
        await activity_service.track_activity(
            db, user.id, "user.updated",
            description="User details updated"
        )
        
        return user

user_service = UserService()
