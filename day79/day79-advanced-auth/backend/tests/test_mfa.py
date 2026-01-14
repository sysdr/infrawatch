import pytest
from app.auth.mfa import MFAService

def test_generate_totp_secret():
    secret = MFAService.generate_totp_secret()
    assert len(secret) == 32
    assert secret.isupper()

def test_verify_totp():
    service = MFAService()
    secret = service.generate_totp_secret()
    
    import pyotp
    totp = pyotp.TOTP(secret)
    current_token = totp.now()
    
    assert service.verify_totp(secret, current_token) == True

def test_generate_backup_codes():
    codes = MFAService.generate_backup_codes(10)
    assert len(codes) == 10
    assert all("code" in c and "hash" in c for c in codes)
