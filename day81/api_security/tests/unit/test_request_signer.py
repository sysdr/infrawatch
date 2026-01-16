import pytest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from security.request_signer import RequestSigner

def test_signature_generation():
    secret = "test_secret_key"
    timestamp = "1704672000"
    method = "POST"
    path = "/api/test"
    body = '{"data": "value"}'
    
    signature = RequestSigner.generate_signature(secret, timestamp, method, path, body)
    
    assert len(signature) == 64  # SHA256 hex = 64 chars
    assert isinstance(signature, str)

def test_signature_verification_valid():
    secret = "test_secret_key"
    timestamp = str(int(time.time()))
    method = "POST"
    path = "/api/test"
    body = '{"data": "value"}'
    
    signature = RequestSigner.generate_signature(secret, timestamp, method, path, body)
    
    is_valid, error = RequestSigner.verify_signature(
        secret, timestamp, method, path, body, signature
    )
    
    assert is_valid is True
    assert error is None

def test_signature_verification_invalid():
    secret = "test_secret_key"
    timestamp = str(int(time.time()))
    method = "POST"
    path = "/api/test"
    body = '{"data": "value"}'
    
    wrong_signature = "invalid_signature_12345"
    
    is_valid, error = RequestSigner.verify_signature(
        secret, timestamp, method, path, body, wrong_signature
    )
    
    assert is_valid is False
    assert "mismatch" in error.lower()

def test_signature_verification_expired():
    secret = "test_secret_key"
    timestamp = str(int(time.time()) - 600)  # 10 minutes ago
    method = "POST"
    path = "/api/test"
    body = '{"data": "value"}'
    
    signature = RequestSigner.generate_signature(secret, timestamp, method, path, body)
    
    is_valid, error = RequestSigner.verify_signature(
        secret, timestamp, method, path, body, signature, max_age=300  # 5 min max
    )
    
    assert is_valid is False
    assert "too old" in error.lower()
