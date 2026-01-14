import pytest
from app.auth.device import DeviceService

def test_generate_fingerprint():
    device_data = {
        "userAgent": "Mozilla/5.0",
        "language": "en-US",
        "platform": "Linux",
        "screen": "1920x1080",
        "timezone": "America/New_York"
    }
    
    fingerprint1 = DeviceService.generate_fingerprint(device_data)
    fingerprint2 = DeviceService.generate_fingerprint(device_data)
    
    assert fingerprint1 == fingerprint2
    assert len(fingerprint1) == 64

def test_calculate_trust_score():
    device_history = {
        "first_seen": None,
        "success_rate": 0.95,
        "failed_attempts": 1
    }
    
    score = DeviceService.calculate_trust_score(device_history)
    assert 0 <= score <= 100
