import asyncio
from typing import Dict, Tuple
from datetime import datetime, timedelta
import redis

class RiskAssessmentService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def assess_login_risk(self, user_id: str, ip: str, device_id: str, 
                                location: Dict) -> Tuple[int, str]:
        """Assess risk score for login attempt"""
        
        # Run all checks in parallel
        results = await asyncio.gather(
            self._check_ip_reputation(ip),
            self._check_velocity(user_id),
            self._check_device_trust(user_id, device_id),
            self._check_location_anomaly(user_id, location),
            self._check_time_anomaly(user_id)
        )
        
        ip_score, velocity_score, device_score, location_score, time_score = results
        
        # Calculate weighted risk score
        risk_score = int(
            ip_score * 0.30 +
            velocity_score * 0.25 +
            device_score * 0.20 +
            location_score * 0.15 +
            time_score * 0.10
        )
        
        action = self._determine_action(risk_score)
        
        return risk_score, action
    
    async def _check_ip_reputation(self, ip: str) -> int:
        """Check IP reputation (0=good, 100=bad)"""
        # Check if IP is in blocklist
        if self.redis.sismember("ip_blocklist", ip):
            return 100
        
        # Check if IP is known VPN/proxy
        if self._is_vpn_ip(ip):
            return 40
        
        # Check previous successful logins from this IP
        success_count = self.redis.get(f"ip_success:{ip}")
        if success_count and int(success_count) > 10:
            return 10
        
        return 30  # Unknown IP - moderate risk
    
    async def _check_velocity(self, user_id: str) -> int:
        """Check for rapid failed login attempts"""
        # Count failed attempts in last 5 minutes
        key = f"failed_attempts:{user_id}"
        attempts = self.redis.zcount(
            key,
            (datetime.utcnow() - timedelta(minutes=5)).timestamp(),
            datetime.utcnow().timestamp()
        )
        
        if attempts >= 5:
            return 100
        elif attempts >= 3:
            return 60
        elif attempts >= 1:
            return 30
        
        return 0
    
    async def _check_device_trust(self, user_id: str, device_id: str) -> int:
        """Check device trust level"""
        # Check if device is known
        device_data = self.redis.get(f"device:{user_id}:{device_id}")
        if not device_data:
            return 50  # New device - moderate risk
        
        # Parse device trust score
        import json
        device = json.loads(device_data)
        trust_score = device.get("trust_score", 50)
        
        # Invert trust score to risk score
        return 100 - trust_score
    
    async def _check_location_anomaly(self, user_id: str, location: Dict) -> int:
        """Check for impossible travel or unusual location"""
        # Get last known location
        last_location_data = self.redis.get(f"last_location:{user_id}")
        if not last_location_data:
            return 20  # First login - low risk
        
        import json
        last_location = json.loads(last_location_data)
        
        # Check for impossible travel
        distance = self._calculate_distance(
            last_location.get("lat", 0), 
            last_location.get("lon", 0),
            location.get("lat", 0), 
            location.get("lon", 0)
        )
        
        time_diff = (datetime.utcnow() - datetime.fromisoformat(
            last_location.get("timestamp", datetime.utcnow().isoformat())
        )).total_seconds()
        
        # If travel speed > 800 km/h (impossible)
        if time_diff > 0 and (distance / (time_diff / 3600)) > 800:
            return 100
        
        # Check if country changed
        if last_location.get("country") != location.get("country"):
            return 60
        
        return 10
    
    async def _check_time_anomaly(self, user_id: str) -> int:
        """Check for unusual login time"""
        current_hour = datetime.utcnow().hour
        
        # Get user's typical login hours
        typical_hours = self.redis.smembers(f"typical_hours:{user_id}")
        
        if not typical_hours:
            return 10  # No history - low risk
        
        typical_hours = [int(h) for h in typical_hours]
        
        # Check if current hour is unusual (outside ±3 hours of typical)
        is_typical = any(
            abs(current_hour - h) <= 3 or abs(current_hour - h) >= 21
            for h in typical_hours
        )
        
        return 10 if is_typical else 40
    
    def _determine_action(self, risk_score: int) -> str:
        """Determine required action based on risk score"""
        if risk_score >= 81:
            return "block"
        elif risk_score >= 61:
            return "require_email_verification"
        elif risk_score >= 31:
            return "require_mfa"
        else:
            return "allow"
    
    @staticmethod
    def _is_vpn_ip(ip: str) -> bool:
        """Check if IP is known VPN/proxy"""
        # Simplified check - in production, use service like IPHub
        vpn_ranges = ["10.", "172.16.", "192.168."]
        return any(ip.startswith(prefix) for prefix in vpn_ranges)
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates (km)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Haversine formula
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
    
    def record_failed_attempt(self, user_id: str):
        """Record failed login attempt"""
        key = f"failed_attempts:{user_id}"
        self.redis.zadd(key, {str(datetime.utcnow().timestamp()): datetime.utcnow().timestamp()})
        self.redis.expire(key, 300)  # 5 minutes
    
    def clear_failed_attempts(self, user_id: str):
        """Clear failed attempts after successful login"""
        self.redis.delete(f"failed_attempts:{user_id}")
