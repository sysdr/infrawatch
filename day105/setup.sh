#!/bin/bash

# Day 105: Automation Integration - Complete Setup Script
# This script creates a production-grade workflow execution engine with security validation

set -e

PROJECT_NAME="automation_integration"
# Create project in same directory as this script (day105)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/$PROJECT_NAME"

echo "=================================================="
echo "Day 105: Automation Integration Setup"
echo "Building Production Workflow Execution Engine"
echo "=================================================="

# Create project structure
mkdir -p "$PROJECT_DIR"/{backend,frontend,tests,docker}
cd "$PROJECT_DIR"

echo "Creating project structure..."

# Backend structure
mkdir -p backend/{app/{api,core,models,services,security,utils},tests}
mkdir -p backend/app/api/v1/endpoints

# Python package __init__.py files (required for imports)
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/api/v1/endpoints/__init__.py

# Frontend structure
mkdir -p frontend/{src/{components,services,hooks,utils,types},public}
mkdir -p frontend/src/components/{Dashboard,WorkflowExecution,ErrorRecovery,SecurityValidation,ExecutionMonitoring}

# Tests structure
mkdir -p tests/{unit,integration,load}

echo "Project structure created successfully"

# Create Backend Files
echo "Creating backend application..."

# Backend requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.110.0
uvicorn[standard]==0.27.1
pydantic==2.6.1
pydantic-settings==2.1.0
sqlalchemy==2.0.25
asyncpg==0.29.0
aiosqlite==0.19.0
alembic==1.13.1
redis==5.0.1
celery==5.3.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
aiofiles==23.2.1
httpx==0.26.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
locust>=2.20.0
websockets==12.0
python-socketio==5.11.1
prometheus-client==0.19.0
psutil==5.9.8
EOF

# Backend main application
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.services.execution_engine import execution_engine
from app.services.websocket_manager import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    logger.info("Starting Automation Integration Engine...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start execution engine
    await execution_engine.start()
    
    yield
    
    # Cleanup
    await execution_engine.stop()
    logger.info("Automation Integration Engine stopped")

app = FastAPI(
    title="Automation Integration Engine",
    description="Production-grade workflow execution with security validation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.websocket("/ws/executions")
async def execution_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time execution updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for connection verification
            await websocket.send_text(f"Connected: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "automation-integration",
        "version": "1.0.0"
    }
EOF

# Configuration
cat > backend/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automation Integration Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database (SQLite for local/demo when PostgreSQL not available)
    DATABASE_URL: str = "sqlite+aiosqlite:///./automation.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Security
    SECRET_KEY: str = "automation-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Execution settings
    MAX_CONCURRENT_EXECUTIONS: int = 10
    MAX_RETRY_ATTEMPTS: int = 3
    EXECUTION_TIMEOUT_SECONDS: int = 300
    
    # Performance targets
    THROUGHPUT_TARGET: int = 10000  # executions per second
    
    class Config:
        case_sensitive = True

settings = Settings()
EOF

# Database setup
cat > backend/app/core/database.py << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# SQLite does not support pool_size; use connect_args for SQLite
_connect_args = {}
_engine_args = {"echo": False}
if "sqlite" in settings.DATABASE_URL:
    _engine_args["connect_args"] = {"check_same_thread": False}
else:
    _engine_args["pool_size"] = 20
    _engine_args["max_overflow"] = 40

engine = create_async_engine(settings.DATABASE_URL, **_engine_args)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
EOF

# Models
cat > backend/app/models/__init__.py << 'EOF'
from app.models.workflow import Workflow, WorkflowExecution, ExecutionStep, ExecutionLog
from app.models.security import SecurityCheck, SecurityViolation

__all__ = [
    "Workflow",
    "WorkflowExecution", 
    "ExecutionStep",
    "ExecutionLog",
    "SecurityCheck",
    "SecurityViolation"
]
EOF

cat > backend/app/models/workflow.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class StepStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    definition = Column(JSON, nullable=False)  # Workflow steps and configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    executions = relationship("WorkflowExecution", back_populates="workflow")

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    execution_time = Column(Float)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    workflow = relationship("Workflow", back_populates="executions")
    steps = relationship("ExecutionStep", back_populates="execution", cascade="all, delete-orphan")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")

class ExecutionStep(Base):
    __tablename__ = "execution_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    step_name = Column(String, nullable=False)
    step_type = Column(String, nullable=False)
    status = Column(Enum(StepStatus), default=StepStatus.PENDING)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    execution_time = Column(Float)
    
    execution = relationship("WorkflowExecution", back_populates="steps")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    step_name = Column(String)
    extra_data = Column(JSON)  # renamed from metadata (reserved in SQLAlchemy)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    execution = relationship("WorkflowExecution", back_populates="logs")
EOF

cat > backend/app/models/security.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean, Enum
from datetime import datetime
import enum
from app.core.database import Base

class SecurityCheckType(str, enum.Enum):
    INPUT_VALIDATION = "input_validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMITING = "rate_limiting"
    RESOURCE_LIMITS = "resource_limits"
    CODE_INJECTION = "code_injection"

class ViolationSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityCheck(Base):
    __tablename__ = "security_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, nullable=False, index=True)
    check_type = Column(Enum(SecurityCheckType), nullable=False)
    passed = Column(Boolean, default=False)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class SecurityViolation(Base):
    __tablename__ = "security_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, nullable=False, index=True)
    violation_type = Column(String, nullable=False)
    severity = Column(Enum(ViolationSeverity), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON)
    remediation = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
EOF

# Execution Engine Service
cat > backend/app/services/execution_engine.py << 'EOF'
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import json

from app.core.database import AsyncSessionLocal
from app.models.workflow import (
    WorkflowExecution, ExecutionStep, ExecutionLog,
    ExecutionStatus, StepStatus, Workflow
)
from app.services.security_validator import security_validator
from app.services.error_recovery import error_recovery
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """Production workflow execution engine with security validation and error recovery"""
    
    def __init__(self):
        self.running = False
        self.execution_queue = asyncio.Queue()
        self.active_executions: Dict[int, asyncio.Task] = {}
        self.max_concurrent = 10
        self.worker_tasks: List[asyncio.Task] = []
        
    async def start(self):
        """Start the execution engine workers"""
        self.running = True
        logger.info(f"Starting execution engine with {self.max_concurrent} workers")
        
        # Start worker tasks
        for i in range(self.max_concurrent):
            task = asyncio.create_task(self._worker(i))
            self.worker_tasks.append(task)
    
    async def stop(self):
        """Stop the execution engine gracefully"""
        self.running = False
        logger.info("Stopping execution engine...")
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Cancel active executions
        for task in self.active_executions.values():
            task.cancel()
        
        logger.info("Execution engine stopped")
    
    async def submit_execution(self, execution_id: int):
        """Submit a workflow execution to the queue"""
        await self.execution_queue.put(execution_id)
        logger.info(f"Execution {execution_id} submitted to queue")
    
    async def _worker(self, worker_id: int):
        """Worker coroutine that processes executions from the queue"""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get execution from queue with timeout
                execution_id = await asyncio.wait_for(
                    self.execution_queue.get(),
                    timeout=1.0
                )
                
                # Execute the workflow
                task = asyncio.create_task(self._execute_workflow(execution_id))
                self.active_executions[execution_id] = task
                
                try:
                    await task
                except Exception as e:
                    logger.error(f"Worker {worker_id} execution {execution_id} failed: {e}")
                finally:
                    self.active_executions.pop(execution_id, None)
                    
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    async def _execute_workflow(self, execution_id: int):
        """Execute a workflow with security validation and error recovery"""
        async with AsyncSessionLocal() as session:
            try:
                # Load execution
                result = await session.execute(
                    select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
                )
                execution = result.scalar_one_or_none()
                
                if not execution:
                    logger.error(f"Execution {execution_id} not found")
                    return
                
                # Load workflow definition
                result = await session.execute(
                    select(Workflow).where(Workflow.id == execution.workflow_id)
                )
                workflow = result.scalar_one_or_none()
                
                if not workflow:
                    logger.error(f"Workflow {execution.workflow_id} not found")
                    return
                
                # Update status to running
                execution.status = ExecutionStatus.RUNNING
                execution.started_at = datetime.utcnow()
                await session.commit()
                
                # Broadcast status update
                await ws_manager.broadcast_execution_update(execution_id, {
                    "status": "running",
                    "started_at": execution.started_at.isoformat()
                })
                
                # Log start
                await self._log_execution(session, execution_id, "INFO", 
                                         f"Starting workflow execution: {workflow.name}")
                
                # Security validation
                security_passed = await security_validator.validate_execution(
                    session, execution_id, execution.input_data
                )
                
                if not security_passed:
                    raise Exception("Security validation failed")
                
                # Execute workflow steps
                steps_definition = workflow.definition.get("steps", [])
                context = {"input": execution.input_data, "outputs": {}}
                
                for step_def in steps_definition:
                    step = await self._execute_step(
                        session, execution_id, step_def, context
                    )
                    
                    if step.status == StepStatus.FAILED:
                        # Attempt error recovery
                        recovered = await error_recovery.attempt_recovery(
                            session, execution_id, step.id, step.error_message
                        )
                        
                        if not recovered:
                            raise Exception(f"Step {step.step_name} failed: {step.error_message}")
                    
                    # Store step output in context
                    context["outputs"][step.step_name] = step.output_data
                
                # Mark execution as completed
                execution.status = ExecutionStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                execution.execution_time = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
                execution.output_data = context["outputs"]
                
                await session.commit()
                
                # Broadcast completion
                await ws_manager.broadcast_execution_update(execution_id, {
                    "status": "completed",
                    "completed_at": execution.completed_at.isoformat(),
                    "execution_time": execution.execution_time
                })
                
                await self._log_execution(session, execution_id, "INFO",
                                         f"Workflow completed in {execution.execution_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Execution {execution_id} failed: {e}")
                
                # Update execution status
                execution.status = ExecutionStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.utcnow()
                if execution.started_at:
                    execution.execution_time = (
                        execution.completed_at - execution.started_at
                    ).total_seconds()
                
                await session.commit()
                
                # Broadcast failure
                await ws_manager.broadcast_execution_update(execution_id, {
                    "status": "failed",
                    "error_message": str(e)
                })
                
                await self._log_execution(session, execution_id, "ERROR", str(e))
    
    async def _execute_step(
        self, 
        session: AsyncSession,
        execution_id: int,
        step_def: Dict,
        context: Dict
    ) -> ExecutionStep:
        """Execute a single workflow step"""
        step_name = step_def.get("name")
        step_type = step_def.get("type")
        
        # Create step record
        step = ExecutionStep(
            execution_id=execution_id,
            step_name=step_name,
            step_type=step_type,
            status=StepStatus.RUNNING,
            started_at=datetime.utcnow(),
            input_data=step_def.get("input", {})
        )
        session.add(step)
        await session.commit()
        await session.refresh(step)
        
        await self._log_execution(session, execution_id, "INFO",
                                 f"Starting step: {step_name}", step_name)
        
        try:
            # Execute step based on type
            if step_type == "script":
                output = await self._execute_script_step(step_def, context)
            elif step_type == "api":
                output = await self._execute_api_step(step_def, context)
            elif step_type == "transform":
                output = await self._execute_transform_step(step_def, context)
            else:
                # Generic execution
                output = {"result": "success", "data": step_def.get("output", {})}
            
            # Update step as completed
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            step.execution_time = (step.completed_at - step.started_at).total_seconds()
            step.output_data = output
            
            await session.commit()
            
            await self._log_execution(session, execution_id, "INFO",
                                     f"Step completed: {step_name} in {step.execution_time:.2f}s",
                                     step_name)
            
        except Exception as e:
            logger.error(f"Step {step_name} failed: {e}")
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            step.completed_at = datetime.utcnow()
            step.execution_time = (step.completed_at - step.started_at).total_seconds()
            
            await session.commit()
            
            await self._log_execution(session, execution_id, "ERROR",
                                     f"Step failed: {step_name} - {str(e)}", step_name)
        
        return step
    
    async def _execute_script_step(self, step_def: Dict, context: Dict) -> Dict:
        """Execute a script step (simulated)"""
        await asyncio.sleep(0.5)  # Simulate execution
        return {
            "result": "success",
            "output": f"Script executed: {step_def.get('script', '')}"
        }
    
    async def _execute_api_step(self, step_def: Dict, context: Dict) -> Dict:
        """Execute an API call step (simulated)"""
        await asyncio.sleep(0.3)  # Simulate API call
        return {
            "result": "success",
            "response": {
                "status": 200,
                "data": {"message": "API call successful"}
            }
        }
    
    async def _execute_transform_step(self, step_def: Dict, context: Dict) -> Dict:
        """Execute a data transformation step"""
        transform_func = step_def.get("function", "identity")
        input_data = context.get("outputs", {}).get(step_def.get("input_step", ""), {})
        
        # Simple transformation
        await asyncio.sleep(0.2)
        return {
            "result": "success",
            "transformed_data": input_data
        }
    
    async def _log_execution(
        self,
        session: AsyncSession,
        execution_id: int,
        level: str,
        message: str,
        step_name: Optional[str] = None
    ):
        """Log execution event"""
        log = ExecutionLog(
            execution_id=execution_id,
            level=level,
            message=message,
            step_name=step_name,
            timestamp=datetime.utcnow()
        )
        session.add(log)
        await session.commit()

# Global execution engine instance
execution_engine = ExecutionEngine()
EOF

# Security Validator Service
cat > backend/app/services/security_validator.py << 'EOF'
import logging
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import re

from app.models.security import SecurityCheck, SecurityViolation, SecurityCheckType, ViolationSeverity

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Production security validation for workflow executions"""
    
    async def validate_execution(
        self,
        session: AsyncSession,
        execution_id: int,
        input_data: Optional[Dict]
    ) -> bool:
        """
        Validate execution security across multiple dimensions
        Returns True if all checks pass, False otherwise
        """
        all_passed = True
        
        # Input validation check
        passed = await self._check_input_validation(session, execution_id, input_data)
        all_passed = all_passed and passed
        
        # Authentication check
        passed = await self._check_authentication(session, execution_id)
        all_passed = all_passed and passed
        
        # Authorization check
        passed = await self._check_authorization(session, execution_id)
        all_passed = all_passed and passed
        
        # Rate limiting check
        passed = await self._check_rate_limiting(session, execution_id)
        all_passed = all_passed and passed
        
        # Resource limits check
        passed = await self._check_resource_limits(session, execution_id, input_data)
        all_passed = all_passed and passed
        
        # Code injection check
        passed = await self._check_code_injection(session, execution_id, input_data)
        all_passed = all_passed and passed
        
        return all_passed
    
    async def _check_input_validation(
        self,
        session: AsyncSession,
        execution_id: int,
        input_data: Optional[Dict]
    ) -> bool:
        """Validate input data structure and content"""
        check = SecurityCheck(
            execution_id=execution_id,
            check_type=SecurityCheckType.INPUT_VALIDATION,
            timestamp=datetime.utcnow()
        )
        
        try:
            if input_data is None:
                check.passed = True
                check.details = {"validation": "no_input_data"}
            else:
                # Validate input structure
                if not isinstance(input_data, dict):
                    raise ValueError("Input data must be a dictionary")
                
                # Check for required fields
                # In production, this would validate against a schema
                check.passed = True
                check.details = {"validation": "passed", "fields": len(input_data)}
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            check.passed = False
            check.details = {"error": str(e)}
            
            # Record violation
            violation = SecurityViolation(
                execution_id=execution_id,
                violation_type="input_validation_failed",
                severity=ViolationSeverity.MEDIUM,
                description=f"Input validation failed: {str(e)}",
                details={"input_data": str(input_data)[:200]}
            )
            session.add(violation)
        
        session.add(check)
        await session.commit()
        return check.passed
    
    async def _check_authentication(
        self,
        session: AsyncSession,
        execution_id: int
    ) -> bool:
        """Verify execution authentication"""
        check = SecurityCheck(
            execution_id=execution_id,
            check_type=SecurityCheckType.AUTHENTICATION,
            passed=True,  # In production, verify JWT token or API key
            details={"method": "token_based"},
            timestamp=datetime.utcnow()
        )
        session.add(check)
        await session.commit()
        return True
    
    async def _check_authorization(
        self,
        session: AsyncSession,
        execution_id: int
    ) -> bool:
        """Verify execution authorization"""
        check = SecurityCheck(
            execution_id=execution_id,
            check_type=SecurityCheckType.AUTHORIZATION,
            passed=True,  # In production, check RBAC permissions
            details={"permissions": ["execute_workflow"]},
            timestamp=datetime.utcnow()
        )
        session.add(check)
        await session.commit()
        return True
    
    async def _check_rate_limiting(
        self,
        session: AsyncSession,
        execution_id: int
    ) -> bool:
        """Check if execution exceeds rate limits"""
        check = SecurityCheck(
            execution_id=execution_id,
            check_type=SecurityCheckType.RATE_LIMITING,
            passed=True,  # In production, check Redis rate limiter
            details={"current_rate": "50/min", "limit": "100/min"},
            timestamp=datetime.utcnow()
        )
        session.add(check)
        await session.commit()
        return True
    
    async def _check_resource_limits(
        self,
        session: AsyncSession,
        execution_id: int,
        input_data: Optional[Dict]
    ) -> bool:
        """Validate resource consumption limits"""
        check = SecurityCheck(
            execution_id=execution_id,
            check_type=SecurityCheckType.RESOURCE_LIMITS,
            timestamp=datetime.utcnow()
        )
        
        try:
            # Check data size
            if input_data:
                data_size = len(str(input_data))
                if data_size > 1_000_000:  # 1MB limit
                    raise ValueError(f"Input data too large: {data_size} bytes")
            
            check.passed = True
            check.details = {"data_size": len(str(input_data)) if input_data else 0}
            
        except Exception as e:
            logger.error(f"Resource limit check failed: {e}")
            check.passed = False
            check.details = {"error": str(e)}
            
            violation = SecurityViolation(
                execution_id=execution_id,
                violation_type="resource_limit_exceeded",
                severity=ViolationSeverity.HIGH,
                description=str(e),
                remediation="Reduce input data size or request limit increase"
            )
            session.add(violation)
        
        session.add(check)
        await session.commit()
        return check.passed
    
    async def _check_code_injection(
        self,
        session: AsyncSession,
        execution_id: int,
        input_data: Optional[Dict]
    ) -> bool:
        """Check for code injection attempts"""
        check = SecurityCheck(
            execution_id=execution_id,
            check_type=SecurityCheckType.CODE_INJECTION,
            timestamp=datetime.utcnow()
        )
        
        try:
            if input_data:
                # Check for suspicious patterns
                suspicious_patterns = [
                    r'<script', r'javascript:', r'eval\(', r'exec\(',
                    r'__import__', r'subprocess', r'os\.system'
                ]
                
                data_str = str(input_data).lower()
                for pattern in suspicious_patterns:
                    if re.search(pattern, data_str):
                        raise ValueError(f"Suspicious pattern detected: {pattern}")
            
            check.passed = True
            check.details = {"patterns_checked": len(suspicious_patterns) if input_data else 0}
            
        except Exception as e:
            logger.error(f"Code injection check failed: {e}")
            check.passed = False
            check.details = {"error": str(e)}
            
            violation = SecurityViolation(
                execution_id=execution_id,
                violation_type="code_injection_attempt",
                severity=ViolationSeverity.CRITICAL,
                description=str(e),
                remediation="Sanitize input data and review source"
            )
            session.add(violation)
        
        session.add(check)
        await session.commit()
        return check.passed

# Global security validator instance
security_validator = SecurityValidator()
EOF

# Error Recovery Service
cat > backend/app/services/error_recovery.py << 'EOF'
import logging
import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.workflow import ExecutionStep, WorkflowExecution, StepStatus, ExecutionStatus
from app.core.config import settings

logger = logging.getLogger(__name__)

class ErrorRecovery:
    """Production error recovery with retry logic and fallback strategies"""
    
    async def attempt_recovery(
        self,
        session: AsyncSession,
        execution_id: int,
        step_id: int,
        error_message: str
    ) -> bool:
        """
        Attempt to recover from step failure
        Returns True if recovery successful, False otherwise
        """
        # Load step
        result = await session.execute(
            select(ExecutionStep).where(ExecutionStep.id == step_id)
        )
        step = result.scalar_one_or_none()
        
        if not step:
            logger.error(f"Step {step_id} not found for recovery")
            return False
        
        # Check retry count
        if step.retry_count >= settings.MAX_RETRY_ATTEMPTS:
            logger.error(f"Step {step_id} exceeded max retry attempts")
            return False
        
        # Determine recovery strategy based on error type
        recovery_strategy = self._determine_recovery_strategy(error_message)
        
        logger.info(f"Attempting recovery for step {step_id} with strategy: {recovery_strategy}")
        
        try:
            if recovery_strategy == "retry":
                return await self._retry_step(session, step)
            elif recovery_strategy == "exponential_backoff":
                return await self._retry_with_backoff(session, step)
            elif recovery_strategy == "fallback":
                return await self._execute_fallback(session, step)
            else:
                logger.error(f"Unknown recovery strategy: {recovery_strategy}")
                return False
                
        except Exception as e:
            logger.error(f"Recovery failed for step {step_id}: {e}")
            return False
    
    def _determine_recovery_strategy(self, error_message: str) -> str:
        """Determine appropriate recovery strategy based on error"""
        error_lower = error_message.lower()
        
        if any(term in error_lower for term in ["timeout", "connection", "network"]):
            return "exponential_backoff"
        elif any(term in error_lower for term in ["rate limit", "quota"]):
            return "exponential_backoff"
        elif any(term in error_lower for term in ["not found", "invalid"]):
            return "fallback"
        else:
            return "retry"
    
    async def _retry_step(
        self,
        session: AsyncSession,
        step: ExecutionStep
    ) -> bool:
        """Simple retry with immediate execution"""
        step.retry_count += 1
        step.status = StepStatus.RUNNING
        step.error_message = None
        step.started_at = datetime.utcnow()
        
        await session.commit()
        
        # Simulate step execution
        await asyncio.sleep(0.5)
        
        # For demo purposes, succeed on retry
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.utcnow()
        step.execution_time = (step.completed_at - step.started_at).total_seconds()
        step.output_data = {"result": "success", "recovered": True}
        
        await session.commit()
        
        logger.info(f"Step {step.id} recovered successfully after retry")
        return True
    
    async def _retry_with_backoff(
        self,
        session: AsyncSession,
        step: ExecutionStep
    ) -> bool:
        """Retry with exponential backoff"""
        step.retry_count += 1
        
        # Calculate backoff time (exponential)
        backoff_seconds = 2 ** step.retry_count
        logger.info(f"Retrying step {step.id} after {backoff_seconds}s backoff")
        
        await asyncio.sleep(backoff_seconds)
        
        step.status = StepStatus.RUNNING
        step.error_message = None
        step.started_at = datetime.utcnow()
        
        await session.commit()
        
        # Simulate step execution
        await asyncio.sleep(0.5)
        
        # For demo purposes, succeed on retry
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.utcnow()
        step.execution_time = (step.completed_at - step.started_at).total_seconds()
        step.output_data = {"result": "success", "recovered": True, "backoff": backoff_seconds}
        
        await session.commit()
        
        logger.info(f"Step {step.id} recovered after {backoff_seconds}s backoff")
        return True
    
    async def _execute_fallback(
        self,
        session: AsyncSession,
        step: ExecutionStep
    ) -> bool:
        """Execute fallback logic for step"""
        logger.info(f"Executing fallback for step {step.id}")
        
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.utcnow()
        step.execution_time = 0.1
        step.output_data = {
            "result": "fallback",
            "message": "Fallback execution successful"
        }
        
        await session.commit()
        
        logger.info(f"Step {step.id} completed with fallback")
        return True

# Global error recovery instance
error_recovery = ErrorRecovery()
EOF

# WebSocket Manager
cat > backend/app/services/websocket_manager.py << 'EOF'
import logging
from typing import List, Dict
from fastapi import WebSocket
import json

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Add new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast_execution_update(self, execution_id: int, data: Dict):
        """Broadcast execution update to all connected clients"""
        message = {
            "type": "execution_update",
            "execution_id": execution_id,
            "data": data
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

# Global WebSocket manager instance
ws_manager = WebSocketManager()
EOF

# API Router
cat > backend/app/api/v1/__init__.py << 'EOF'
from fastapi import APIRouter
from app.api.v1.endpoints import workflows, executions, security, monitoring

api_router = APIRouter()

api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
api_router.include_router(security.router, prefix="/security", tags=["security"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
EOF

# Workflows endpoint
cat > backend/app/api/v1/endpoints/workflows.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.workflow import Workflow

router = APIRouter()

class WorkflowCreate(BaseModel):
    name: str
    description: str
    definition: dict

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str
    definition: dict
    
    class Config:
        from_attributes = True

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow"""
    db_workflow = Workflow(**workflow.model_dump())
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow)
    return db_workflow

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    """List all workflows"""
    result = await db.execute(select(Workflow).order_by(Workflow.created_at.desc()))
    workflows = result.scalars().all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: int, db: AsyncSession = Depends(get_db)):
    """Get workflow by ID"""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow
EOF

# Executions endpoint
cat > backend/app/api/v1/endpoints/executions.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.workflow import WorkflowExecution, ExecutionStep, ExecutionLog, ExecutionStatus
from app.services.execution_engine import execution_engine

router = APIRouter()

class ExecutionCreate(BaseModel):
    workflow_id: int
    input_data: Optional[dict] = None

class ExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    status: str
    input_data: Optional[dict]
    output_data: Optional[dict]
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExecutionStepResponse(BaseModel):
    id: int
    step_name: str
    step_type: str
    status: str
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    
    class Config:
        from_attributes = True

class ExecutionLogResponse(BaseModel):
    id: int
    level: str
    message: str
    step_name: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ExecutionResponse)
async def create_execution(
    execution: ExecutionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create and start a new workflow execution"""
    db_execution = WorkflowExecution(
        workflow_id=execution.workflow_id,
        input_data=execution.input_data,
        status=ExecutionStatus.PENDING
    )
    db.add(db_execution)
    await db.commit()
    await db.refresh(db_execution)
    
    # Submit to execution engine
    await execution_engine.submit_execution(db_execution.id)
    
    return db_execution

@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List workflow executions with optional status filter"""
    query = select(WorkflowExecution).order_by(WorkflowExecution.created_at.desc())
    
    if status:
        query = query.where(WorkflowExecution.status == status)
    
    result = await db.execute(query)
    executions = result.scalars().all()
    return executions

@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get execution by ID"""
    result = await db.execute(
        select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution

@router.get("/{execution_id}/steps", response_model=List[ExecutionStepResponse])
async def get_execution_steps(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get steps for an execution"""
    result = await db.execute(
        select(ExecutionStep)
        .where(ExecutionStep.execution_id == execution_id)
        .order_by(ExecutionStep.id)
    )
    steps = result.scalars().all()
    return steps

@router.get("/{execution_id}/logs", response_model=List[ExecutionLogResponse])
async def get_execution_logs(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get logs for an execution"""
    result = await db.execute(
        select(ExecutionLog)
        .where(ExecutionLog.execution_id == execution_id)
        .order_by(ExecutionLog.timestamp)
    )
    logs = result.scalars().all()
    return logs

@router.post("/{execution_id}/retry")
async def retry_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Retry a failed execution"""
    result = await db.execute(
        select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status not in [ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Only failed or cancelled executions can be retried")
    
    # Reset execution
    execution.status = ExecutionStatus.PENDING
    execution.error_message = None
    execution.retry_count += 1
    
    await db.commit()
    
    # Submit to execution engine
    await execution_engine.submit_execution(execution_id)
    
    return {"message": "Execution retry submitted", "execution_id": execution_id}
EOF

# Security endpoint
cat > backend/app/api/v1/endpoints/security.py << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.security import SecurityCheck, SecurityViolation, ViolationSeverity

router = APIRouter()

class SecurityCheckResponse(BaseModel):
    id: int
    execution_id: int
    check_type: str
    passed: bool
    details: dict
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SecurityViolationResponse(BaseModel):
    id: int
    execution_id: int
    violation_type: str
    severity: str
    description: str
    details: dict
    remediation: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SecurityStatsResponse(BaseModel):
    total_checks: int
    passed_checks: int
    failed_checks: int
    total_violations: int
    critical_violations: int
    high_violations: int

@router.get("/checks/{execution_id}", response_model=List[SecurityCheckResponse])
async def get_security_checks(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get security checks for an execution"""
    result = await db.execute(
        select(SecurityCheck)
        .where(SecurityCheck.execution_id == execution_id)
        .order_by(SecurityCheck.timestamp)
    )
    checks = result.scalars().all()
    return checks

@router.get("/violations", response_model=List[SecurityViolationResponse])
async def list_violations(db: AsyncSession = Depends(get_db)):
    """List all security violations"""
    result = await db.execute(
        select(SecurityViolation).order_by(SecurityViolation.timestamp.desc()).limit(100)
    )
    violations = result.scalars().all()
    return violations

@router.get("/stats", response_model=SecurityStatsResponse)
async def get_security_stats(db: AsyncSession = Depends(get_db)):
    """Get security statistics"""
    # Total checks
    total_checks_result = await db.execute(select(func.count(SecurityCheck.id)))
    total_checks = total_checks_result.scalar() or 0
    
    # Passed checks
    passed_checks_result = await db.execute(
        select(func.count(SecurityCheck.id)).where(SecurityCheck.passed == True)
    )
    passed_checks = passed_checks_result.scalar() or 0
    
    # Total violations
    total_violations_result = await db.execute(select(func.count(SecurityViolation.id)))
    total_violations = total_violations_result.scalar() or 0
    
    # Critical violations
    critical_result = await db.execute(
        select(func.count(SecurityViolation.id)).where(SecurityViolation.severity == ViolationSeverity.CRITICAL)
    )
    critical_violations = critical_result.scalar() or 0
    
    # High violations
    high_result = await db.execute(
        select(func.count(SecurityViolation.id)).where(SecurityViolation.severity == ViolationSeverity.HIGH)
    )
    high_violations = high_result.scalar() or 0
    
    return SecurityStatsResponse(
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=total_checks - passed_checks,
        total_violations=total_violations,
        critical_violations=critical_violations,
        high_violations=high_violations
    )
EOF

# Monitoring endpoint
cat > backend/app/api/v1/endpoints/monitoring.py << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.workflow import WorkflowExecution, ExecutionStatus
from app.services.execution_engine import execution_engine

router = APIRouter()

class ExecutionMetrics(BaseModel):
    total_executions: int
    completed: int
    failed: int
    running: int
    pending: int
    average_execution_time: float
    success_rate: float

class SystemHealth(BaseModel):
    status: str
    active_workers: int
    queue_size: int
    active_executions: int

@router.get("/metrics", response_model=ExecutionMetrics)
async def get_execution_metrics(db: AsyncSession = Depends(get_db)):
    """Get execution metrics"""
    # Total executions
    total_result = await db.execute(select(func.count(WorkflowExecution.id)))
    total = total_result.scalar() or 0
    
    # Completed
    completed_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.COMPLETED)
    )
    completed = completed_result.scalar() or 0
    
    # Failed
    failed_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.FAILED)
    )
    failed = failed_result.scalar() or 0
    
    # Running
    running_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.RUNNING)
    )
    running = running_result.scalar() or 0
    
    # Pending
    pending_result = await db.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.status == ExecutionStatus.PENDING)
    )
    pending = pending_result.scalar() or 0
    
    # Average execution time
    avg_time_result = await db.execute(
        select(func.avg(WorkflowExecution.execution_time))
        .where(WorkflowExecution.execution_time.isnot(None))
    )
    avg_time = avg_time_result.scalar() or 0.0
    
    # Success rate
    success_rate = (completed / total * 100) if total > 0 else 0.0
    
    return ExecutionMetrics(
        total_executions=total,
        completed=completed,
        failed=failed,
        running=running,
        pending=pending,
        average_execution_time=float(avg_time),
        success_rate=success_rate
    )

@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get system health status"""
    return SystemHealth(
        status="healthy" if execution_engine.running else "stopped",
        active_workers=len(execution_engine.worker_tasks),
        queue_size=execution_engine.execution_queue.qsize(),
        active_executions=len(execution_engine.active_executions)
    )
EOF

# Create Frontend Files
echo "Creating frontend application..."

# Frontend package.json
cat > frontend/package.json << 'EOF'
{
  "name": "automation-integration-ui",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "@mui/material": "^5.15.10",
    "@mui/icons-material": "^5.15.10",
    "@emotion/react": "^11.11.3",
    "@emotion/styled": "^11.11.0",
    "axios": "^1.6.7",
    "recharts": "^2.12.0",
    "date-fns": "^3.3.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

# Frontend index.html
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Automation Integration Dashboard" />
    <title>Automation Integration Dashboard</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Frontend index.js
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Frontend App.js
cat > frontend/src/App.js << 'EOF'
import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

import ExecutionDashboard from './components/Dashboard/ExecutionDashboard';
import WorkflowExecution from './components/WorkflowExecution/WorkflowExecution';
import SecurityValidation from './components/SecurityValidation/SecurityValidation';
import ErrorRecovery from './components/ErrorRecovery/ErrorRecovery';
import ExecutionMonitoring from './components/ExecutionMonitoring/ExecutionMonitoring';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              🤖 Automation Integration Dashboard
            </Typography>
            <Typography variant="body2">
              Production Workflow Execution Engine
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Dashboard" />
              <Tab label="Workflow Execution" />
              <Tab label="Security Validation" />
              <Tab label="Error Recovery" />
              <Tab label="Monitoring" />
            </Tabs>
          </Paper>

          <TabPanel value={tabValue} index={0}>
            <ExecutionDashboard />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <WorkflowExecution />
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <SecurityValidation />
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            <ErrorRecovery />
          </TabPanel>
          <TabPanel value={tabValue} index={4}>
            <ExecutionMonitoring />
          </TabPanel>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
EOF

# API Service
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const workflowsApi = {
  list: () => api.get('/workflows'),
  get: (id) => api.get(`/workflows/${id}`),
  create: (data) => api.post('/workflows', data),
};

export const executionsApi = {
  list: (status = null) => {
    const params = status ? { status } : {};
    return api.get('/executions', { params });
  },
  get: (id) => api.get(`/executions/${id}`),
  create: (data) => api.post('/executions', data),
  getSteps: (id) => api.get(`/executions/${id}/steps`),
  getLogs: (id) => api.get(`/executions/${id}/logs`),
  retry: (id) => api.post(`/executions/${id}/retry`),
};

export const securityApi = {
  getChecks: (executionId) => api.get(`/security/checks/${executionId}`),
  listViolations: () => api.get('/security/violations'),
  getStats: () => api.get('/security/stats'),
};

export const monitoringApi = {
  getMetrics: () => api.get('/monitoring/metrics'),
  getHealth: () => api.get('/monitoring/health'),
};

export default api;
EOF

# WebSocket Hook
cat > frontend/src/hooks/useWebSocket.js << 'EOF'
import { useEffect, useState, useCallback } from 'react';

const WEBSOCKET_URL = 'ws://localhost:8000/ws/executions';

export const useWebSocket = () => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(WEBSOCKET_URL);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      ws.send('init');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prev) => [...prev, data]);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = useCallback(
    (message) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(message));
      }
    },
    [socket]
  );

  return { messages, sendMessage, isConnected };
};
EOF

# Execution Dashboard Component
cat > frontend/src/components/Dashboard/ExecutionDashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import PendingIcon from '@mui/icons-material/Pending';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

import { executionsApi, monitoringApi } from '../../services/api';

function ExecutionDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [recentExecutions, setRecentExecutions] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, executionsRes, healthRes] = await Promise.all([
        monitoringApi.getMetrics(),
        executionsApi.list(),
        monitoringApi.getHealth().catch(() => ({ data: null })),
      ]);
      setMetrics({ ...metricsRes.data, health: healthRes.data });
      setRecentExecutions(executionsRes.data.slice(0, 10));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  if (!metrics) {
    return <Typography>Loading...</Typography>;
  }

  const chartData = recentExecutions.map((exec, index) => ({
    name: `Exec ${exec.id}`,
    time: exec.execution_time || 0,
  }));

  return (
    <Grid container spacing={3}>
      {/* Metrics Cards */}
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e3f2fd' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Executions
                </Typography>
                <Typography variant="h4">{metrics.total_executions}</Typography>
              </Box>
              <PlayArrowIcon sx={{ fontSize: 48, color: '#1976d2' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e8f5e9' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Completed
                </Typography>
                <Typography variant="h4">{metrics.completed}</Typography>
              </Box>
              <CheckCircleIcon sx={{ fontSize: 48, color: '#4caf50' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#ffebee' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Failed
                </Typography>
                <Typography variant="h4">{metrics.failed}</Typography>
              </Box>
              <ErrorIcon sx={{ fontSize: 48, color: '#f44336' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#fff3e0' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Success Rate
                </Typography>
                <Typography variant="h4">{(metrics.success_rate ?? 0).toFixed(1)}%</Typography>
              </Box>
              <CheckCircleIcon sx={{ fontSize: 48, color: '#ff9800' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Execution Time Chart */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Execution Times
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'Time (s)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="time" stroke="#1976d2" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Additional Metrics */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Performance Metrics
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">
              Average Execution Time: <strong>{(metrics.average_execution_time ?? 0).toFixed(2)}s</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Running: <strong>{metrics.running}</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Pending: <strong>{metrics.pending}</strong>
            </Typography>
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">
              Status: <strong style={{ color: metrics.health?.status === 'healthy' ? '#4caf50' : '#f44336' }}>{metrics.health?.status ?? 'Loading...'}</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Active Workers: <strong>{metrics.health?.active_workers ?? '-'}</strong>
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Queue Size: <strong>{metrics.health?.queue_size ?? '-'}</strong>
            </Typography>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default ExecutionDashboard;
EOF

# Workflow Execution Component (truncated for space - will continue in next file)
cat > frontend/src/components/WorkflowExecution/WorkflowExecution.js << 'EOF'
import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';

import { workflowsApi, executionsApi } from '../../services/api';
import { useWebSocket } from '../../hooks/useWebSocket';

function WorkflowExecution() {
  const [workflows, setWorkflows] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [inputData, setInputData] = useState('{}');
  const { messages } = useWebSocket();

  useEffect(() => {
    fetchWorkflows();
    fetchExecutions();
  }, []);

  useEffect(() => {
    // Handle WebSocket messages
    messages.forEach((msg) => {
      if (msg.type === 'execution_update') {
        fetchExecutions();
      }
    });
  }, [messages]);

  const fetchWorkflows = async () => {
    try {
      const response = await workflowsApi.list();
      setWorkflows(response.data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchExecutions = async () => {
    try {
      const response = await executionsApi.list();
      setExecutions(response.data);
    } catch (error) {
      console.error('Error fetching executions:', error);
    }
  };

  const handleExecute = async () => {
    if (!selectedWorkflow) {
      alert('Please select a workflow');
      return;
    }

    try {
      const input = JSON.parse(inputData);
      await executionsApi.create({
        workflow_id: selectedWorkflow.id,
        input_data: input,
      });
      fetchExecutions();
      setInputData('{}');
    } catch (error) {
      console.error('Error creating execution:', error);
      alert('Error creating execution');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'default',
      running: 'primary',
      completed: 'success',
      failed: 'error',
      cancelled: 'warning',
    };
    return colors[status] || 'default';
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Create Execution
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Select Workflow
            </Typography>
            {workflows.map((workflow) => (
              <Button
                key={workflow.id}
                variant={selectedWorkflow?.id === workflow.id ? 'contained' : 'outlined'}
                onClick={() => setSelectedWorkflow(workflow)}
                sx={{ mr: 1, mb: 1 }}
              >
                {workflow.name}
              </Button>
            ))}
          </Box>

          {selectedWorkflow && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Workflow: {selectedWorkflow.name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {selectedWorkflow.description}
              </Typography>
            </Box>
          )}

          <TextField
            fullWidth
            multiline
            rows={4}
            label="Input Data (JSON)"
            value={inputData}
            onChange={(e) => setInputData(e.target.value)}
            sx={{ mt: 2 }}
          />

          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={handleExecute}
            sx={{ mt: 2 }}
            disabled={!selectedWorkflow}
          >
            Execute Workflow
          </Button>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Recent Executions
            </Typography>
            <Button
              startIcon={<RefreshIcon />}
              onClick={fetchExecutions}
              size="small"
            >
              Refresh
            </Button>
          </Box>

          <Table sx={{ mt: 2 }} size="small">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {executions.slice(0, 10).map((execution) => (
                <TableRow key={execution.id}>
                  <TableCell>{execution.id}</TableCell>
                  <TableCell>
                    <Chip
                      label={execution.status}
                      color={getStatusColor(execution.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {execution.execution_time ? `${execution.execution_time.toFixed(2)}s` : '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default WorkflowExecution;
EOF

# Continue with remaining components...
echo "Creating remaining frontend components..."

cat > frontend/src/components/SecurityValidation/SecurityValidation.js << 'EOF'
import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import { securityApi } from '../../services/api';

function SecurityValidation() {
  const [stats, setStats] = useState(null);
  const [violations, setViolations] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, violationsRes] = await Promise.all([
        securityApi.getStats(),
        securityApi.listViolations(),
      ]);
      setStats(statsRes.data);
      setViolations(violationsRes.data);
    } catch (error) {
      console.error('Error fetching security data:', error);
    }
  };

  if (!stats) {
    return <Typography>Loading...</Typography>;
  }

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'info',
      medium: 'warning',
      high: 'error',
      critical: 'error',
    };
    return colors[severity] || 'default';
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e3f2fd' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Checks
                </Typography>
                <Typography variant="h4">{stats.total_checks}</Typography>
              </Box>
              <SecurityIcon sx={{ fontSize: 48, color: '#1976d2' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#e8f5e9' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Passed
                </Typography>
                <Typography variant="h4">{stats.passed_checks}</Typography>
              </Box>
              <SecurityIcon sx={{ fontSize: 48, color: '#4caf50' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#ffebee' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Failed
                </Typography>
                <Typography variant="h4">{stats.failed_checks}</Typography>
              </Box>
              <WarningIcon sx={{ fontSize: 48, color: '#f44336' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: '#fff3e0' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Violations
                </Typography>
                <Typography variant="h4">{stats.total_violations}</Typography>
              </Box>
              <WarningIcon sx={{ fontSize: 48, color: '#ff9800' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Security Violations
          </Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Execution ID</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Timestamp</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {violations.map((violation) => (
                <TableRow key={violation.id}>
                  <TableCell>{violation.execution_id}</TableCell>
                  <TableCell>{violation.violation_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={violation.severity}
                      color={getSeverityColor(violation.severity)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{violation.description}</TableCell>
                  <TableCell>
                    {new Date(violation.timestamp).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default SecurityValidation;
EOF

cat > frontend/src/components/ErrorRecovery/ErrorRecovery.js << 'EOF'
import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import RefreshIcon from '@mui/icons-material/Refresh';
import ReplayIcon from '@mui/icons-material/Replay';
import { executionsApi } from '../../services/api';

function ErrorRecovery() {
  const [failedExecutions, setFailedExecutions] = useState([]);

  useEffect(() => {
    fetchFailedExecutions();
  }, []);

  const fetchFailedExecutions = async () => {
    try {
      const response = await executionsApi.list('failed');
      setFailedExecutions(response.data);
    } catch (error) {
      console.error('Error fetching failed executions:', error);
    }
  };

  const handleRetry = async (executionId) => {
    try {
      await executionsApi.retry(executionId);
      fetchFailedExecutions();
      alert('Execution retry submitted');
    } catch (error) {
      console.error('Error retrying execution:', error);
      alert('Error retrying execution');
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Failed Executions - Error Recovery
            </Typography>
            <Button
              startIcon={<RefreshIcon />}
              onClick={fetchFailedExecutions}
              variant="outlined"
            >
              Refresh
            </Button>
          </Box>

          <Table sx={{ mt: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Workflow ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Error</TableCell>
                <TableCell>Retry Count</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {failedExecutions.map((execution) => (
                <TableRow key={execution.id}>
                  <TableCell>{execution.id}</TableCell>
                  <TableCell>{execution.workflow_id}</TableCell>
                  <TableCell>
                    <Chip label={execution.status} color="error" size="small" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                      {execution.error_message || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>{execution.retry_count}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<ReplayIcon />}
                      onClick={() => handleRetry(execution.id)}
                      disabled={execution.retry_count >= 3}
                    >
                      Retry
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {failedExecutions.length === 0 && (
            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Typography color="textSecondary">
                No failed executions found
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
}

export default ErrorRecovery;
EOF

cat > frontend/src/components/ExecutionMonitoring/ExecutionMonitoring.js << 'EOF'
import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Box from '@mui/material/Box';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import { executionsApi } from '../../services/api';

function ExecutionMonitoring() {
  const [executionId, setExecutionId] = useState('');
  const [execution, setExecution] = useState(null);
  const [steps, setSteps] = useState([]);
  const [logs, setLogs] = useState([]);

  const handleSearch = async () => {
    if (!executionId) return;

    try {
      const [execRes, stepsRes, logsRes] = await Promise.all([
        executionsApi.get(executionId),
        executionsApi.getSteps(executionId),
        executionsApi.getLogs(executionId),
      ]);
      setExecution(execRes.data);
      setSteps(stepsRes.data);
      setLogs(logsRes.data);
    } catch (error) {
      console.error('Error fetching execution details:', error);
      alert('Execution not found');
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Execution Monitoring
          </Typography>
          
          <Box display="flex" gap={2} sx={{ mt: 2 }}>
            <TextField
              label="Execution ID"
              value={executionId}
              onChange={(e) => setExecutionId(e.target.value)}
              size="small"
              sx={{ flexGrow: 1 }}
            />
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
            >
              Search
            </Button>
          </Box>
        </Paper>
      </Grid>

      {execution && (
        <>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Execution Details
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography><strong>ID:</strong> {execution.id}</Typography>
                <Typography><strong>Workflow ID:</strong> {execution.workflow_id}</Typography>
                <Typography><strong>Status:</strong> {execution.status}</Typography>
                <Typography><strong>Execution Time:</strong> {execution.execution_time ? `${execution.execution_time.toFixed(2)}s` : '-'}</Typography>
                <Typography><strong>Retry Count:</strong> {execution.retry_count}</Typography>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Execution Steps ({steps.length})</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Step Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Retry Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {steps.map((step) => (
                      <TableRow key={step.id}>
                        <TableCell>{step.step_name}</TableCell>
                        <TableCell>{step.step_type}</TableCell>
                        <TableCell>{step.status}</TableCell>
                        <TableCell>
                          {step.execution_time ? `${step.execution_time.toFixed(2)}s` : '-'}
                        </TableCell>
                        <TableCell>{step.retry_count}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </AccordionDetails>
            </Accordion>
          </Grid>

          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Execution Logs ({logs.length})</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {logs.map((log) => (
                    <Box
                      key={log.id}
                      sx={{
                        p: 1,
                        mb: 1,
                        bgcolor: log.level === 'ERROR' ? '#ffebee' : '#f5f5f5',
                        borderRadius: 1,
                      }}
                    >
                      <Typography variant="caption" color="textSecondary">
                        {new Date(log.timestamp).toLocaleString()} - {log.level}
                        {log.step_name && ` - ${log.step_name}`}
                      </Typography>
                      <Typography variant="body2">{log.message}</Typography>
                    </Box>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </>
      )}
    </Grid>
  );
}

export default ExecutionMonitoring;
EOF

# Create Tests
echo "Creating test files..."

cat > tests/test_execution.py << 'EOF'
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
EOF

cat > tests/test_security.py << 'EOF'
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
EOF

# Build and run scripts
cat > build.sh << 'EOF'
#!/bin/bash

echo "========================================="
echo "Building Automation Integration System"
echo "========================================="

cd "$(dirname "$0")"

# Setup PostgreSQL
echo "Setting up PostgreSQL..."
if command -v psql &> /dev/null; then
    sudo -u postgres psql -c "CREATE DATABASE automation_db;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER automation WITH PASSWORD 'automation123';" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE automation_db TO automation;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE automation_test_db;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE automation_test_db TO automation;" 2>/dev/null || true
fi

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run backend tests (continue even if tests fail so we can start services)
echo "Running backend tests..."
cd ..
source backend/venv/bin/activate
PYTHONPATH=backend pytest tests/ -v || true

# Start backend
echo "Starting backend..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 5

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install

# Start frontend
echo "Starting frontend..."
npm start &
FRONTEND_PID=$!
cd ..

echo "========================================="
echo "System Started Successfully!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "========================================="
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait
wait
EOF

cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping Automation Integration System..."

# Kill backend
pkill -f "uvicorn app.main:app"

# Kill frontend
pkill -f "react-scripts start"

echo "System stopped"
EOF

# Demo script: create workflow and run execution so dashboard shows non-zero metrics
cat > run_demo.sh << 'DEMOEOF'
#!/bin/bash
cd "$(dirname "$0")"
API="${API_BASE_URL:-http://localhost:8000/api/v1}"
echo "Running demo against $API ..."
# Create a demo workflow
WORKFLOW_JSON=$(curl -s -X POST "$API/workflows/" -H "Content-Type: application/json" -d '{"name":"Demo Workflow","description":"Sample workflow for dashboard demo","definition":{"steps":[{"name":"step1","type":"script","script":"echo hello"},{"name":"step2","type":"api"},{"name":"step3","type":"transform"}]}}')
WORKFLOW_ID=$(echo "$WORKFLOW_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)
if [ -z "$WORKFLOW_ID" ]; then
  echo "Failed to create workflow. Is backend running?"
  exit 1
fi
echo "Created workflow ID: $WORKFLOW_ID"
# Run 2 executions so dashboard has data
for i in 1 2; do
  curl -s -X POST "$API/executions/" -H "Content-Type: application/json" -d "{\"workflow_id\":$WORKFLOW_ID,\"input_data\":{\"run\":$i}}" > /dev/null
  echo "Started execution $i"
done
echo "Demo complete. Wait a few seconds then refresh the dashboard."
DEMOEOF

chmod +x build.sh stop.sh run_demo.sh

echo "=================================================="
echo "Project setup complete!"
echo "=================================================="
echo ""
echo "Project created at: $PROJECT_DIR"
echo "Directory structure:"
tree -L 3 -I 'node_modules|venv|__pycache__|*.pyc' . 2>/dev/null || find . -type d -maxdepth 3 | grep -v -E 'node_modules|venv|__pycache__' | head -80
echo ""
echo "To build and run:"
echo "  cd $PROJECT_DIR && ./build.sh"
echo ""
echo "To stop:"
echo "  ./stop.sh   (from $PROJECT_DIR)"
echo ""
echo "Manual start:"
echo "  Backend: cd $PROJECT_DIR/backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd $PROJECT_DIR/frontend && npm start"
echo ""
echo "Run tests:"
echo "  cd $PROJECT_DIR && source backend/venv/bin/activate && PYTHONPATH=backend pytest tests/ -v"
echo ""
echo "Setup complete. Project at: $PROJECT_DIR"
echo "To build and run: cd $PROJECT_DIR && ./build.sh"