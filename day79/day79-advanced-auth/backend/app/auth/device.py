import hashlib
import json
from typing import Dict
from datetime import datetime

class DeviceService:
    @staticmethod
    def generate_fingerprint(device_data: Dict) -> str:
        """Generate unique device fingerprint from device attributes"""
        # Combine key attributes
        fingerprint_data = {
            "userAgent": device_data.get("userAgent", ""),
            "language": device_data.get("language", ""),
            "platform": device_data.get("platform", ""),
            "screen": device_data.get("screen", ""),
            "timezone": device_data.get("timezone", ""),
            "canvas": device_data.get("canvas", ""),
            "webgl": device_data.get("webgl", "")
        }
        
        # Create SHA256 hash
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    @staticmethod
    def calculate_trust_score(device_history: Dict) -> int:
        """Calculate device trust score based on history"""
        score = 50  # Base score
        
        # Increase score for device age
        if device_history.get("first_seen"):
            days_known = (datetime.utcnow() - device_history["first_seen"]).days
            score += min(days_known, 30)  # Max +30 for age
        
        # Increase score for successful logins
        success_rate = device_history.get("success_rate", 0)
        score += int(success_rate * 20)  # Max +20 for 100% success
        
        # Decrease score for failed attempts
        failed_attempts = device_history.get("failed_attempts", 0)
        score -= min(failed_attempts * 5, 30)  # Max -30 for failures
        
        return max(0, min(100, score))
    
    @staticmethod
    def extract_device_info(user_agent: str, ip_address: str) -> Dict:
        """Extract device information from user agent and IP"""
        return {
            "browser": DeviceService._extract_browser(user_agent),
            "os": DeviceService._extract_os(user_agent),
            "device_type": DeviceService._extract_device_type(user_agent),
            "ip_address": ip_address
        }
    
    @staticmethod
    def _extract_browser(user_agent: str) -> str:
        """Extract browser from user agent"""
        if "Chrome" in user_agent:
            return "Chrome"
        elif "Firefox" in user_agent:
            return "Firefox"
        elif "Safari" in user_agent:
            return "Safari"
        elif "Edge" in user_agent:
            return "Edge"
        return "Unknown"
    
    @staticmethod
    def _extract_os(user_agent: str) -> str:
        """Extract OS from user agent"""
        if "Windows" in user_agent:
            return "Windows"
        elif "Mac OS" in user_agent:
            return "macOS"
        elif "Linux" in user_agent:
            return "Linux"
        elif "Android" in user_agent:
            return "Android"
        elif "iOS" in user_agent:
            return "iOS"
        return "Unknown"
    
    @staticmethod
    def _extract_device_type(user_agent: str) -> str:
        """Extract device type from user agent"""
        if "Mobile" in user_agent:
            return "Mobile"
        elif "Tablet" in user_agent:
            return "Tablet"
        return "Desktop"
