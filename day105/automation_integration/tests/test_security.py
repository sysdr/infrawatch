import pytest
import pytest_asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.security_validator import security_validator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_automation.db"

@pytest_asyncio.fixture
async def test_session():
    """Create test database session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_input_validation_pass(test_session):
    """Test successful input validation"""
    result = await security_validator._check_input_validation(
        test_session, 1, {"key": "value"}
    )
    assert result is True

@pytest.mark.asyncio
async def test_input_validation_fail(test_session):
    """Test failed input validation"""
    result = await security_validator._check_input_validation(
        test_session, 1, "invalid_input"
    )
    assert result is False

@pytest.mark.asyncio
async def test_resource_limits(test_session):
    """Test resource limit validation"""
    # Small input should pass
    result = await security_validator._check_resource_limits(
        test_session, 1, {"data": "small"}
    )
    assert result is True
    
    # Large input should fail
    large_data = {"data": "x" * 2_000_000}
    result = await security_validator._check_resource_limits(
        test_session, 1, large_data
    )
    assert result is False

@pytest.mark.asyncio
async def test_code_injection_detection(test_session):
    """Test code injection detection"""
    # Safe input
    result = await security_validator._check_code_injection(
        test_session, 1, {"safe": "data"}
    )
    assert result is True
    
    # Malicious input
    result = await security_validator._check_code_injection(
        test_session, 1, {"script": "<script>alert('xss')</script>"}
    )
    assert result is False
