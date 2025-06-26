import asyncio
import json
import time
import random
from typing import Optional, Dict
from datetime import datetime, timedelta

class AccountLockoutManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.max_attempts = 5
        self.base_lockout_time = 60  # 1 minute base
        self.max_lockout_time = 3600  # 1 hour max

    async def get_attempt_count(self, identifier: str) -> int:
        """Get current attempt count for identifier"""
        key = f"auth_attempts:{identifier}"
        count = await self.redis.get(key)
        return int(count) if count else 0

    async def get_lockout_info(self, identifier: str) -> Optional[Dict]:
        """Get lockout information for identifier"""
        key = f"lockout:{identifier}"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def is_locked_out(self, identifier: str) -> bool:
        """Check if identifier is currently locked out"""
        lockout_info = await self.get_lockout_info(identifier)
        if not lockout_info:
            return False
            
        unlock_time = datetime.fromisoformat(lockout_info['unlock_time'])
        return datetime.now() < unlock_time

    async def calculate_lockout_duration(self, attempt_count: int) -> int:
        """Calculate lockout duration using exponential backoff with jitter"""
        if attempt_count <= 3:
            return 0
        
        # Exponential backoff: 2^(attempts-3) * base_time
        base_duration = min(
            self.base_lockout_time * (2 ** (attempt_count - 4)),
            self.max_lockout_time
        )
        
        # Add jitter (±20% random variation)
        jitter = base_duration * 0.2 * (random.random() - 0.5)
        return int(base_duration + jitter)

    async def record_failed_attempt(self, identifier: str) -> Dict:
        """Record a failed authentication attempt"""
        attempt_key = f"auth_attempts:{identifier}"
        lockout_key = f"lockout:{identifier}"
        
        # Increment attempt count
        current_attempts = await self.redis.incr(attempt_key)
        await self.redis.expire(attempt_key, 3600)  # Expire in 1 hour
        
        # Calculate lockout duration
        lockout_duration = await self.calculate_lockout_duration(current_attempts)
        
        result = {
            'attempts': current_attempts,
            'max_attempts': self.max_attempts,
            'locked_out': False,
            'lockout_duration': lockout_duration,
            'remaining_attempts': max(0, self.max_attempts - current_attempts)
        }
        
        # Apply lockout if necessary
        if current_attempts >= self.max_attempts and lockout_duration > 0:
            unlock_time = datetime.now() + timedelta(seconds=lockout_duration)
            lockout_data = {
                'locked_at': datetime.now().isoformat(),
                'unlock_time': unlock_time.isoformat(),
                'attempt_count': current_attempts,
                'duration': lockout_duration
            }
            
            await self.redis.setex(
                lockout_key, 
                lockout_duration, 
                json.dumps(lockout_data)
            )
            
            result['locked_out'] = True
            result['unlock_time'] = unlock_time.isoformat()
        
        return result

    async def record_successful_attempt(self, identifier: str):
        """Clear attempts and lockouts after successful authentication"""
        attempt_key = f"auth_attempts:{identifier}"
        lockout_key = f"lockout:{identifier}"
        
        await self.redis.delete(attempt_key)
        await self.redis.delete(lockout_key)

    async def get_lockout_status(self, identifier: str) -> Dict:
        """Get comprehensive lockout status"""
        attempts = await self.get_attempt_count(identifier)
        lockout_info = await self.get_lockout_info(identifier)
        is_locked = await self.is_locked_out(identifier)
        
        result = {
            'attempts': attempts,
            'max_attempts': self.max_attempts,
            'is_locked_out': is_locked,
            'remaining_attempts': max(0, self.max_attempts - attempts)
        }
        
        if lockout_info:
            result.update({
                'locked_at': lockout_info['locked_at'],
                'unlock_time': lockout_info['unlock_time'],
                'lockout_duration': lockout_info['duration']
            })
            
        return result
