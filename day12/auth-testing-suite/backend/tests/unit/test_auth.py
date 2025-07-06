import pytest
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate

class TestAuthService:
    
    def test_password_validation(self):
        """Test password strength validation"""
        auth_service = AuthService()
        
        # Test weak passwords
        weak_passwords = ["password", "12345678", "Password", "password123"]
        for password in weak_passwords:
            with pytest.raises(ValueError):
                auth_service.validate_password(password)
        
        # Test strong password
        strong_password = "StrongPass123!"
        assert auth_service.validate_password(strong_password) is True
    
    def test_email_validation(self):
        """Test email format validation"""
        auth_service = AuthService()
        
        # Test valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        for email in valid_emails:
            assert auth_service.validate_email(email) is True
        
        # Test invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com"
        ]
        for email in invalid_emails:
            assert auth_service.validate_email(email) is False
    
    def test_user_creation_schema(self):
        """Test user creation schema validation"""
        valid_user_data = UserCreate(
            email="test@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User"
        )
        assert valid_user_data.email == "test@example.com"
        assert valid_user_data.first_name == "Test"
        assert valid_user_data.last_name == "User" 