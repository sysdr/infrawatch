import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from passlib.hash import bcrypt
from typing import List, Dict

class MFAService:
    @staticmethod
    def generate_totp_secret() -> str:
        """Generate a random base32 secret for TOTP"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(secret: str, user_email: str, issuer: str = "AuthSystem") -> str:
        """Generate QR code for TOTP secret"""
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=user_email, issuer_name=issuer)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_totp(secret: str, token: str, valid_window: int = 1) -> bool:
        """Verify TOTP token with time window tolerance"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[Dict[str, str]]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append({
                "code": code,
                "hash": bcrypt.hash(code),
                "used": False
            })
        return codes
    
    @staticmethod
    def verify_backup_code(stored_hash: str, provided_code: str) -> bool:
        """Verify backup code against stored hash"""
        return bcrypt.verify(provided_code, stored_hash)
    
    @staticmethod
    def generate_sms_code() -> str:
        """Generate 6-digit SMS verification code"""
        return str(secrets.randbelow(1000000)).zfill(6)
