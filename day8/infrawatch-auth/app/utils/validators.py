import re
from typing import List, Optional
import unicodedata

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    # Pattern that prevents double dots and ensures proper format
    pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    # Additional check for double dots
    if '..' in email:
        return False
    return True

def validate_password(password: str) -> tuple[bool, List[str]]:
    """Validate password strength"""
    errors = []
    
    if not password:
        errors.append("Password is required")
        return False, errors
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>?]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors

def validate_name(name: Optional[str]) -> bool:
    """Validate name format"""
    if not name:
        return True  # Optional field
    name = name.strip()
    if not (1 <= len(name) <= 100):
        return False
    allowed = set(" -'.")
    for char in name:
        if char in allowed:
            continue
        if unicodedata.category(char).startswith('L'):
            continue
        return False
    return True
