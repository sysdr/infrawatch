from datetime import datetime, timedelta
from typing import List, Optional
import logging
from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)

# Consent purpose bits (64 purposes max)
CONSENT_PURPOSES = {
    "ANALYTICS": 1 << 0,
    "MARKETING": 1 << 1,
    "PERSONALIZATION": 1 << 2,
    "ADVERTISING": 1 << 3,
    "THIRD_PARTY_SHARING": 1 << 4,
    "RESEARCH": 1 << 5,
    "PRODUCT_IMPROVEMENT": 1 << 6,
    "CUSTOMER_SUPPORT": 1 << 7,
}

class PrivacyService:
    def __init__(self):
        self.consent_cache_ttl = 3600  # 1 hour
    
    async def grant_consent(self, user_id: int, purposes: List[str]) -> int:
        """Grant consent for specific purposes using bitfield"""
        consent_bitfield = 0
        
        for purpose in purposes:
            if purpose in CONSENT_PURPOSES:
                consent_bitfield |= CONSENT_PURPOSES[purpose]
        
        # Cache in Redis for fast lookups
        redis = await get_redis()
        await redis.setex(
            f"consent:{user_id}",
            self.consent_cache_ttl,
            str(consent_bitfield)
        )
        
        logger.info(f"Granted consent for user {user_id}: {purposes}")
        return consent_bitfield
    
    async def revoke_consent(self, user_id: int, purposes: List[str]) -> int:
        """Revoke consent for specific purposes"""
        # Get current consent
        redis = await get_redis()
        current_consent = await redis.get(f"consent:{user_id}")
        consent_bitfield = int(current_consent) if current_consent else 0
        
        # Remove purposes
        for purpose in purposes:
            if purpose in CONSENT_PURPOSES:
                consent_bitfield &= ~CONSENT_PURPOSES[purpose]
        
        # Update cache
        await redis.setex(
            f"consent:{user_id}",
            self.consent_cache_ttl,
            str(consent_bitfield)
        )
        
        logger.info(f"Revoked consent for user {user_id}: {purposes}")
        return consent_bitfield
    
    async def check_consent(self, user_id: int, purpose: str) -> bool:
        """Check if user has granted consent for a purpose"""
        if purpose not in CONSENT_PURPOSES:
            return False
        
        redis = await get_redis()
        consent = await redis.get(f"consent:{user_id}")
        
        if not consent:
            return False
        
        consent_bitfield = int(consent)
        has_consent = (consent_bitfield & CONSENT_PURPOSES[purpose]) != 0
        
        # Log access for audit
        await self.log_consent_check(user_id, purpose, has_consent)
        
        return has_consent
    
    async def log_consent_check(self, user_id: int, purpose: str, granted: bool):
        """Log consent check for audit trail"""
        redis = await get_redis()
        log_entry = {
            "user_id": user_id,
            "purpose": purpose,
            "granted": granted,
            "timestamp": datetime.now().isoformat()
        }
        await redis.lpush(f"consent_audit:{user_id}", str(log_entry))
        await redis.ltrim(f"consent_audit:{user_id}", 0, 999)  # Keep last 1000 entries
    
    async def get_user_consents(self, user_id: int) -> dict:
        """Get all consents for a user"""
        redis = await get_redis()
        consent = await redis.get(f"consent:{user_id}")
        
        if not consent:
            return {}
        
        consent_bitfield = int(consent)
        consents = {}
        
        for purpose, bit in CONSENT_PURPOSES.items():
            consents[purpose] = (consent_bitfield & bit) != 0
        
        return consents

# Global instance
privacy_service = PrivacyService()
