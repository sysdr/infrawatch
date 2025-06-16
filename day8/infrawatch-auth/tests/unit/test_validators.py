import pytest
from app.utils.validators import validate_email, validate_password, validate_name

class TestValidators:
    
    def test_valid_emails(self):
        """Test valid email formats"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test+tag@example.org',
            'first.last@subdomain.example.com'
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_invalid_emails(self):
        """Test invalid email formats"""
        invalid_emails = [
            '',
            'notanemail',
            '@example.com',
            'test@',
            'test..test@example.com',
            'test@example',
            None
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False
    
    def test_valid_passwords(self):
        """Test valid password formats"""
        valid_passwords = [
            'TestPass123!',
            'MySecure@Pass1',
            'C0mpl3x#P@ssw0rd'
        ]
        
        for password in valid_passwords:
            is_valid, errors = validate_password(password)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_invalid_passwords(self):
        """Test invalid password formats"""
        test_cases = [
            ('', ['Password is required']),
            ('short', ['Password must be at least 8 characters long']),
            ('nouppercase1!', ['Password must contain at least one uppercase letter']),
            ('NOLOWERCASE1!', ['Password must contain at least one lowercase letter']),
            ('NoNumbers!', ['Password must contain at least one digit']),
            ('NoSpecial123', ['Password must contain at least one special character'])
        ]
        
        for password, expected_errors in test_cases:
            is_valid, errors = validate_password(password)
            assert is_valid is False
            assert len(errors) >= len(expected_errors)
    
    def test_valid_names(self):
        """Test valid name formats"""
        valid_names = [
            'John',
            'Mary-Jane',
            "O'Connor",
            'Jean-Pierre',
            'José',
            None,  # Optional field
            ''     # Empty string should be valid (optional)
        ]
        
        for name in valid_names:
            assert validate_name(name) is True
    
    def test_invalid_names(self):
        """Test invalid name formats"""
        invalid_names = [
            'John123',
            'Name@Email',
            'Too$pecial',
            'A' * 101  # Too long
        ]
        
        for name in invalid_names:
            assert validate_name(name) is False
