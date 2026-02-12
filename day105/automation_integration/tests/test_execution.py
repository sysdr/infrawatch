import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import Base
from app.models.workflow import Workflow, WorkflowExecution, ExecutionStatus
from app.services.execution_engine import execution_engine

# Test database URL (SQLite for portability)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_automation.db"

@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create test database session"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_workflow_creation(test_session):
    """Test workflow creation"""
    workflow = Workflow(
        name="Test Workflow",
        description="Test workflow for automation",
        definition={
            "steps": [
                {"name": "step1", "type": "script", "script": "echo 'test'"}
            ]
        }
    )
    test_session.add(workflow)
    await test_session.commit()
    
    assert workflow.id is not None
    assert workflow.name == "Test Workflow"

@pytest.mark.asyncio
async def test_execution_creation(test_session):
    """Test execution creation"""
    workflow = Workflow(
        name="Test Workflow",
        description="Test workflow",
        definition={"steps": []}
    )
    test_session.add(workflow)
    await test_session.commit()
    
    execution = WorkflowExecution(
        workflow_id=workflow.id,
        input_data={"test": "data"},
        status=ExecutionStatus.PENDING
    )
    test_session.add(execution)
    await test_session.commit()
    
    assert execution.id is not None
    assert execution.status == ExecutionStatus.PENDING

@pytest.mark.asyncio
async def test_execution_engine_start_stop():
    """Test execution engine lifecycle"""
    await execution_engine.start()
    assert execution_engine.running is True
    assert len(execution_engine.worker_tasks) > 0
    
    await execution_engine.stop()
    assert execution_engine.running is False
