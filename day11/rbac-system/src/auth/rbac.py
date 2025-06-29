from functools import wraps
from typing import List, Union
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.auth.utils import verify_token, check_permission
from src.models.user import User
import redis
import json
import os

# Redis for caching permissions
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Extract current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def require_permissions(permissions: Union[str, List[str]]):
    """Decorator to require specific permissions for an endpoint"""
    if isinstance(permissions, str):
        permissions = [permissions]
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (FastAPI dependency injection)
            current_user = None
            db = None
            
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                elif hasattr(value, 'query'):  # SQLAlchemy session
                    db = value
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependencies not properly configured"
                )
            
            # Check cached permissions first
            cache_key = f"user_permissions:{current_user.id}"
            try:
                cached_permissions = redis_client.get(cache_key)
                if cached_permissions:
                    user_permissions = json.loads(cached_permissions)
                else:
                    from src.auth.utils import get_user_permissions
                    user_permissions = get_user_permissions(db, current_user.id)
                    # Cache for 5 minutes
                    redis_client.setex(cache_key, 300, json.dumps(user_permissions))
            except:
                # Fallback to database if Redis is unavailable
                from src.auth.utils import get_user_permissions
                user_permissions = get_user_permissions(db, current_user.id)
            
            # Check if user has all required permissions
            missing_permissions = [p for p in permissions if p not in user_permissions]
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(roles: Union[str, List[str]]):
    """Decorator to require specific roles for an endpoint"""
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependencies not properly configured"
                )
            
            user_roles = [role.name for role in current_user.roles if role.is_active]
            if not any(role in user_roles for role in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role not found. Need one of: {', '.join(roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Helper function to invalidate user permission cache
def invalidate_user_permissions_cache(user_id: int):
    """Invalidate cached permissions when user roles change"""
    cache_key = f"user_permissions:{user_id}"
    try:
        redis_client.delete(cache_key)
    except:
        pass  # Redis unavailable, permissions will be fetched from DB
