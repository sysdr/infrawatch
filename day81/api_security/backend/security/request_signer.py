import hmac
import hashlib
import time
from typing import Optional, Tuple
from app.config import get_settings

settings = get_settings()

class RequestSigner:
    
    @staticmethod
    def generate_signature(secret: str, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate HMAC-SHA256 signature for request"""
        content = f"{timestamp}{method}{path}{body}"
        
        signature = hmac.new(
            secret.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    @staticmethod
    def verify_signature(
        secret: str,
        timestamp: str,
        method: str,
        path: str,
        body: str,
        provided_signature: str,
        max_age: int = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify request signature
        Returns: (is_valid, error_message)
        """
        max_age = max_age or settings.signature_max_age
        
        # Check timestamp age (replay protection)
        try:
            timestamp_int = int(timestamp)
        except (ValueError, TypeError):
            return False, "Invalid timestamp format"
        
        current_time = int(time.time())
        age = current_time - timestamp_int
        
        if abs(age) > max_age:
            return False, f"Timestamp too old or in future (age: {age}s, max: {max_age}s)"
        
        # Generate expected signature
        expected_signature = RequestSigner.generate_signature(
            secret, timestamp, method, path, body
        )
        
        # Constant-time comparison (timing attack protection)
        is_valid = hmac.compare_digest(provided_signature, expected_signature)
        
        if not is_valid:
            return False, "Signature mismatch"
        
        return True, None
