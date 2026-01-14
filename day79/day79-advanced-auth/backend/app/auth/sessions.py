import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class SessionService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def create_session(self, user_id: str, device_id: str, ip: str, 
                      user_agent: str, mfa_verified: bool = False) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "device_id": device_id,
            "ip_address": ip,
            "user_agent": user_agent,
            "mfa_verified": mfa_verified,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        # Store session with 24-hour TTL
        self.redis.setex(
            f"session:{user_id}:{session_id}",
            86400,
            json.dumps(session_data)
        )
        
        # Add to user's session set
        self.redis.sadd(f"user_sessions:{user_id}", session_id)
        
        return session_id
    
    def get_session(self, user_id: str, session_id: str) -> Optional[Dict]:
        """Retrieve session data"""
        data = self.redis.get(f"session:{user_id}:{session_id}")
        if data:
            return json.loads(data)
        return None
    
    def update_activity(self, user_id: str, session_id: str):
        """Update last activity timestamp"""
        session_data = self.get_session(user_id, session_id)
        if session_data:
            session_data["last_activity"] = datetime.utcnow().isoformat()
            self.redis.setex(
                f"session:{user_id}:{session_id}",
                86400,
                json.dumps(session_data)
            )
    
    def revoke_session(self, user_id: str, session_id: str):
        """Revoke specific session"""
        self.redis.delete(f"session:{user_id}:{session_id}")
        self.redis.srem(f"user_sessions:{user_id}", session_id)
    
    def revoke_all_sessions(self, user_id: str):
        """Revoke all user sessions"""
        session_ids = self.redis.smembers(f"user_sessions:{user_id}")
        for sid in session_ids:
            self.redis.delete(f"session:{user_id}:{sid}")
        self.redis.delete(f"user_sessions:{user_id}")
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all active sessions for user"""
        session_ids = self.redis.smembers(f"user_sessions:{user_id}")
        sessions = []
        
        for sid in session_ids:
            session_data = self.get_session(user_id, sid)
            if session_data:
                session_data["session_id"] = sid
                sessions.append(session_data)
        
        return sessions
