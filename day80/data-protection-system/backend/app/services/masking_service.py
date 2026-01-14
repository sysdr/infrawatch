import re
import hashlib
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class MaskingService:
    def __init__(self):
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
    
    def mask_email(self, email: str) -> str:
        """Mask email: john.doe@example.com -> j***@example.com"""
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 1:
            masked_local = local
        else:
            masked_local = local[0] + '***'
        
        return f"{masked_local}@{domain}"
    
    def mask_phone(self, phone: str) -> str:
        """Mask phone: 123-456-7890 -> ***-***-7890"""
        if not phone:
            return phone
        
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 4:
            return f"***-***-{digits[-4:]}"
        return "***-***-****"
    
    def mask_ssn(self, ssn: str) -> str:
        """Mask SSN: 123-45-6789 -> ***-**-6789"""
        if not ssn:
            return ssn
        
        parts = ssn.split('-')
        if len(parts) == 3:
            return f"***-**-{parts[2]}"
        return "***-**-****"
    
    def mask_credit_card(self, cc: str) -> str:
        """Mask credit card: 1234-5678-9012-3456 -> ****-****-****-3456"""
        if not cc:
            return cc
        
        digits = re.sub(r'\D', '', cc)
        if len(digits) >= 4:
            return f"****-****-****-{digits[-4:]}"
        return "****-****-****-****"
    
    def mask_ip_address(self, ip: str) -> str:
        """Mask IP: 192.168.1.100 -> 192.168.*.*"""
        if not ip:
            return ip
        
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return "*.*.*.*"
    
    def tokenize(self, value: str, salt: str = "default") -> str:
        """One-way tokenization using SHA-256"""
        if not value:
            return value
        
        hash_input = f"{value}:{salt}".encode()
        token = hashlib.sha256(hash_input).hexdigest()[:16]
        return f"token_{token}"
    
    def mask_text(self, text: str) -> str:
        """Automatically detect and mask PII in text"""
        if not text:
            return text
        
        masked = text
        
        # Mask emails
        masked = re.sub(
            self.patterns["email"],
            lambda m: self.mask_email(m.group(0)),
            masked
        )
        
        # Mask phone numbers
        masked = re.sub(
            self.patterns["phone"],
            lambda m: self.mask_phone(m.group(0)),
            masked
        )
        
        # Mask SSNs
        masked = re.sub(
            self.patterns["ssn"],
            lambda m: self.mask_ssn(m.group(0)),
            masked
        )
        
        # Mask credit cards
        masked = re.sub(
            self.patterns["credit_card"],
            lambda m: self.mask_credit_card(m.group(0)),
            masked
        )
        
        # Mask IPs
        masked = re.sub(
            self.patterns["ip_address"],
            lambda m: self.mask_ip_address(m.group(0)),
            masked
        )
        
        return masked
    
    def mask_dict(self, data: Dict[str, Any], fields_to_mask: list = None) -> Dict[str, Any]:
        """Mask specified fields in a dictionary"""
        if not data:
            return data
        
        masked_data = data.copy()
        
        # Default sensitive fields
        if fields_to_mask is None:
            fields_to_mask = ["email", "phone", "ssn", "credit_card", "password"]
        
        for field in fields_to_mask:
            if field in masked_data:
                value = masked_data[field]
                if isinstance(value, str):
                    if "email" in field.lower():
                        masked_data[field] = self.mask_email(value)
                    elif "phone" in field.lower():
                        masked_data[field] = self.mask_phone(value)
                    elif "ssn" in field.lower():
                        masked_data[field] = self.mask_ssn(value)
                    elif "card" in field.lower() or "credit" in field.lower():
                        masked_data[field] = self.mask_credit_card(value)
                    else:
                        masked_data[field] = "***MASKED***"
        
        return masked_data

# Global instance
masking_service = MaskingService()
