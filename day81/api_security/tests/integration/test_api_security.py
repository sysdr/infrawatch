import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from security.api_key_manager import APIKeyManager
from models.api_key import APIKey

@pytest.mark.asyncio
async def test_api_key_creation(db_session):
    api_key_obj, full_key = await APIKeyManager.create_api_key(
        db=db_session,
        name="Test Key",
        description="Integration test key",
        rate_limit=100,
        rate_window=60
    )
    
    assert api_key_obj.name == "Test Key"
    assert full_key.startswith("sk_live_")
    assert api_key_obj.is_active is True
    assert api_key_obj.is_revoked is False

@pytest.mark.asyncio
async def test_api_key_validation(db_session):
    api_key_obj, full_key = await APIKeyManager.create_api_key(
        db=db_session,
        name="Validation Test Key"
    )
    
    # Valid key
    validated = await APIKeyManager.validate_api_key(db_session, full_key)
    assert validated is not None
    assert validated.key_id == api_key_obj.key_id
    
    # Invalid key
    validated = await APIKeyManager.validate_api_key(db_session, "sk_live_invalid_key")
    assert validated is None

@pytest.mark.asyncio
async def test_api_key_revocation(db_session):
    api_key_obj, full_key = await APIKeyManager.create_api_key(
        db=db_session,
        name="Revocation Test Key"
    )
    
    # Revoke
    success = await APIKeyManager.revoke_api_key(db_session, api_key_obj.key_id)
    assert success is True
    
    # Validation should fail after revocation
    validated = await APIKeyManager.validate_api_key(db_session, full_key)
    assert validated is None
