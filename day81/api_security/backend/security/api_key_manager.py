import secrets
import hashlib
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.api_key import APIKey
from app.config import get_settings

settings = get_settings()

class APIKeyManager:
    
    @staticmethod
    def generate_key_pair(prefix: str = None) -> Tuple[str, str, str]:
        """Generate API key with prefix, key_id, and secret"""
        if prefix is None:
            prefix = settings.api_key_prefix
        
        # Generate random bytes for key_id
        random_bytes = secrets.token_bytes(16)
        key_id = hashlib.sha256(random_bytes).hexdigest()[:16]
        
        # Generate secret
        secret = secrets.token_urlsafe(32)
        
        # Combine into full API key
        full_key = f"{prefix}_{key_id}_{secret}"
        
        # Hash the secret for storage
        hashed_secret = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()
        
        return full_key, key_id, hashed_secret
    
    @staticmethod
    async def create_api_key(
        db: AsyncSession,
        name: str,
        description: str = "",
        permissions: list = None,
        rate_limit: int = None,
        rate_window: int = None,
        ip_whitelist: list = None,
        expires_in_days: int = None
    ) -> Tuple[APIKey, str]:
        """Create a new API key"""
        
        full_key, key_id, hashed_secret = APIKeyManager.generate_key_pair()
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        elif settings.api_key_expiry_days:
            expires_at = datetime.utcnow() + timedelta(days=settings.api_key_expiry_days)
        
        api_key = APIKey(
            key_id=key_id,
            hashed_secret=hashed_secret,
            prefix=settings.api_key_prefix,
            name=name,
            description=description,
            permissions=permissions or [],
            rate_limit=rate_limit or settings.rate_limit_requests,
            rate_window=rate_window or settings.rate_limit_window,
            ip_whitelist=ip_whitelist or [],
            expires_at=expires_at
        )
        
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        
        return api_key, full_key
    
    @staticmethod
    async def validate_api_key(db: AsyncSession, api_key: str) -> Optional[APIKey]:
        """Validate API key and return APIKey object if valid"""
        try:
            # Format: prefix_keyid_secret (where prefix may contain underscores like "sk_live")
            # Split from the right to handle secrets with underscores
            # Key ID is always 16 hex characters, so find it after the prefix
            if not api_key.startswith(settings.api_key_prefix + "_"):
                return None
            
            # Remove prefix and underscore to get keyid_secret
            # Format: sk_live_<16-char-keyid>_<secret>
            prefix_len = len(settings.api_key_prefix) + 1  # +1 for underscore after prefix
            keyid_secret = api_key[prefix_len:]
            
            # Key ID is always 16 hex characters, followed by underscore
            # So we need at least 17 characters (16 for key_id + 1 for underscore)
            if len(keyid_secret) < 17:
                return None
            
            # Check if there's an underscore at position 16 (after 16-char key_id)
            if keyid_secret[16] != "_":
                return None
            
            key_id = keyid_secret[:16]
            secret = keyid_secret[17:]  # Skip the underscore after key_id (position 16)
            
            result = await db.execute(
                select(APIKey).where(
                    APIKey.key_id == key_id,
                    APIKey.is_active == True,
                    APIKey.is_revoked == False
                )
            )
            key_obj = result.scalar_one_or_none()
            
            if not key_obj:
                return None
            
            # Check expiration
            if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
                return None
            
            # Verify secret
            if not bcrypt.checkpw(secret.encode(), key_obj.hashed_secret.encode()):
                return None
            
            # Update last used timestamp
            key_obj.last_used_at = datetime.utcnow()
            await db.commit()
            
            return key_obj
            
        except Exception as e:
            return None
    
    @staticmethod
    async def revoke_api_key(db: AsyncSession, key_id: str) -> bool:
        """Revoke an API key"""
        result = await db.execute(
            select(APIKey).where(APIKey.key_id == key_id)
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            return False
        
        api_key.is_revoked = True
        api_key.is_active = False
        api_key.revoked_at = datetime.utcnow()
        
        await db.commit()
        return True
    
    @staticmethod
    async def rotate_api_key(db: AsyncSession, old_key_id: str) -> Tuple[Optional[APIKey], Optional[str]]:
        """Rotate an API key (create new, schedule old for deletion)"""
        result = await db.execute(
            select(APIKey).where(APIKey.key_id == old_key_id)
        )
        old_key = result.scalar_one_or_none()
        
        if not old_key:
            return None, None
        
        # Create new key with same settings
        new_key, full_key = await APIKeyManager.create_api_key(
            db=db,
            name=f"{old_key.name} (Rotated)",
            description=old_key.description,
            permissions=old_key.permissions,
            rate_limit=old_key.rate_limit,
            rate_window=old_key.rate_window,
            ip_whitelist=old_key.ip_whitelist
        )
        
        new_key.rotated_from = old_key.id
        
        # Schedule old key for revocation (24 hour grace period)
        old_key.rotation_scheduled_at = datetime.utcnow() + timedelta(hours=24)
        
        await db.commit()
        await db.refresh(new_key)
        
        return new_key, full_key
