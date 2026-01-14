import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.encryption_service import EncryptionService
from app.services.classification_service import ClassificationService
from app.services.privacy_service import PrivacyService
from app.services.masking_service import MaskingService

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 503]

def test_encrypt_decrypt():
    """Test encryption and decryption"""
    # Encrypt
    encrypt_response = client.post(
        "/api/encryption/encrypt",
        json={"plaintext": "sensitive data", "context": "test"}
    )
    assert encrypt_response.status_code == 200
    encrypted_data = encrypt_response.json()["encrypted_data"]
    
    # Decrypt
    decrypt_response = client.post(
        "/api/encryption/decrypt",
        json={"encrypted_data": encrypted_data}
    )
    assert decrypt_response.status_code == 200
    assert decrypt_response.json()["plaintext"] == "sensitive data"

def test_data_classification():
    """Test data classification"""
    response = client.post(
        "/api/classification/classify",
        json={
            "data": {
                "username": "john_doe",
                "email": "john@example.com",
                "ssn": "123-45-6789",
                "credit_card": "1234-5678-9012-3456"
            }
        }
    )
    assert response.status_code == 200
    classifications = response.json()["classifications"]
    assert classifications["username"]["level"] == "PUBLIC"
    assert classifications["ssn"]["level"] == "RESTRICTED"
    assert classifications["ssn"]["requires_encryption"] == True

def test_consent_management():
    """Test consent grant and check"""
    # Grant consent
    grant_response = client.post(
        "/api/privacy/grant-consent",
        json={"user_id": 1, "purposes": ["ANALYTICS", "MARKETING"]}
    )
    assert grant_response.status_code == 200
    
    # Check consent
    check_response = client.post(
        "/api/privacy/check-consent",
        json={"user_id": 1, "purpose": "ANALYTICS"}
    )
    assert check_response.status_code == 200
    assert check_response.json()["granted"] == True

def test_data_masking():
    """Test PII masking"""
    # Mask email
    response = client.post(
        "/api/masking/mask-email",
        params={"email": "john.doe@example.com"}
    )
    assert response.status_code == 200
    assert "***" in response.json()["masked"]
    
    # Mask text with multiple PII
    text_response = client.post(
        "/api/masking/mask-text",
        json={"text": "Contact john.doe@example.com or call 123-456-7890"}
    )
    assert text_response.status_code == 200
    masked = text_response.json()["masked_text"]
    assert "***" in masked

def test_gdpr_access_request():
    """Test GDPR access request creation"""
    response = client.post(
        "/api/gdpr/access-request",
        json={"user_id": 1}
    )
    assert response.status_code == 200
    assert "request_id" in response.json()
    assert response.json()["status"] == "pending"

def test_encryption_service():
    """Test encryption service directly"""
    service = EncryptionService()
    service.master_key = b'0' * 32
    
    encrypted = service.encrypt("test data", "test_context")
    assert "ciphertext" in encrypted
    assert "nonce" in encrypted
    
    decrypted = service.decrypt(encrypted)
    assert decrypted == "test data"

def test_masking_service():
    """Test masking service patterns"""
    service = MaskingService()
    
    # Test email masking
    assert "***" in service.mask_email("john.doe@example.com")
    
    # Test phone masking
    assert "***" in service.mask_phone("123-456-7890")
    
    # Test SSN masking
    masked_ssn = service.mask_ssn("123-45-6789")
    assert masked_ssn == "***-**-6789"
    
    # Test credit card masking
    masked_cc = service.mask_credit_card("1234-5678-9012-3456")
    assert masked_cc == "****-****-****-3456"

def test_metrics():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert "encryption" in metrics
    assert "classification" in metrics
    assert "privacy" in metrics
    assert "masking" in metrics
    assert "gdpr" in metrics

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
