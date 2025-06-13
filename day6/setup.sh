#!/bin/bash

# Testing Framework Setup - Complete Implementation Script
# Day 6: Distributed Systems Testing Framework
# Creates a production-ready testing environment for log processing system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    log_success "All prerequisites are installed"
}

create_project_structure() {
    log_info "Creating project structure..."
    
    # Main directories
    mkdir -p backend/{src/{models,services,api,utils},tests/{unit,integration,fixtures,factories}}
    mkdir -p frontend/src/{components,services,utils,__tests__}
    mkdir -p config/{test,docker}
    mkdir -p docs
    mkdir -p scripts
    
    log_success "Project structure created"
}

setup_backend_testing() {
    log_info "Setting up backend testing framework..."
    
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Create requirements.txt
    cat > requirements.txt << 'EOF'
# Core dependencies
asyncpg==0.29.0
greenlet==3.0.1
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
psycopg2-binary==2.9.9
redis==5.0.1
sqlalchemy==2.0.23
alembic==1.13.1

# Testing dependencies
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-xdist==3.5.0
pytest-mock==3.12.0
factory-boy==3.3.0
faker==20.1.0
httpx==0.25.2

# Development dependencies
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
EOF
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "Backend dependencies installed"
    
    # Create pytest configuration
    cat > pytest.ini << 'EOF'
[tool:pytest]
minversion = 6.0
addopts = 
    -ra 
    --strict-markers 
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
    --tb=short
testpaths = tests
markers =
    unit: fast isolated tests
    integration: tests requiring real services
    slow: tests taking >1 second
    smoke: basic functionality tests
    performance: performance-related tests
asyncio_mode = auto
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
EOF
    
    # Create conftest.py with fixtures
    cat > tests/conftest.py << 'EOF'
import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from fastapi import FastAPI

from src.models.database import Base
from src.models.log_event import LogEvent
from src.api.main import create_app

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql+asyncpg://test_user:test_password@localhost:5433/test_logs"
)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for each test."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_app() -> FastAPI:
    """Create test FastAPI application."""
    app = create_app()
    return app

@pytest.fixture
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client
EOF
    
    # Create database models
    mkdir -p src/models
    cat > src/models/__init__.py << 'EOF'
# Models package
EOF
    
    cat > src/models/database.py << 'EOF'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://user:password@localhost:5432/logs"
)

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_database_session():
    async with async_session() as session:
        yield session
EOF
    
    cat > src/models/log_event.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base

class LogLevel(PyEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
class LogEvent(Base):
    __tablename__ = "log_events"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    level = Column(Enum(LogLevel), default=LogLevel.INFO)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(255), nullable=True)
    log_metadata = Column(Text, nullable=True)  # Changed from 'metadata'
    
    def __repr__(self):
        return f"<LogEvent(id={self.id}, level={self.level}, message='{self.message[:50]}...')>"
EOF
    
    # Create test factories
    cat > tests/factories/__init__.py << 'EOF'
# Factories package
EOF
    
    cat > tests/factories/log_event_factory.py << 'EOF'
import factory
from factory import Faker
from datetime import datetime, timedelta
import json
import random
from src.models.log_event import LogEvent, LogLevel

class LogEventFactory(factory.Factory):
    class Meta:
        model = LogEvent
    
    id = factory.Sequence(lambda n: n)
    message = Faker('sentence', nb_words=6)
    level = factory.Iterator(LogLevel)
    timestamp = factory.LazyFunction(datetime.utcnow)
    source = Faker('word')
    metadata = factory.LazyFunction(lambda: json.dumps({"user_id": random.randint(1, 1000)}))
    
    @classmethod
    def create_batch_with_timestamps(cls, size=10, start_time=None, interval_seconds=60):
        """Create batch of logs with specific timestamp intervals."""
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=1)
        
        logs = []
        for i in range(size):
            timestamp = start_time + timedelta(seconds=i * interval_seconds)
            logs.append(cls.build(timestamp=timestamp))
        return logs
    
    @classmethod
    def create_error_scenario(cls, error_count=5, normal_count=10):
        """Create realistic error scenario with burst of errors."""
        logs = []
        
        # Normal logs first
        for _ in range(normal_count):
            logs.append(cls.build(level=LogLevel.INFO))
        
        # Then error burst
        error_start = datetime.utcnow()
        for i in range(error_count):
            timestamp = error_start + timedelta(seconds=i * 5)
            logs.append(cls.build(
                level=LogLevel.ERROR,
                message=f"Database connection failed (attempt {i+1})",
                timestamp=timestamp
            ))
        
        return logs
    
    @classmethod
    def create_high_volume_simulation(cls, events_per_minute=100, duration_minutes=1):
        """Simulate high-volume log generation."""
        total_events = events_per_minute * duration_minutes
        interval_seconds = 60 / events_per_minute
        
        return cls.create_batch_with_timestamps(
            size=total_events,
            interval_seconds=interval_seconds
        )
EOF
    
    # Create unit tests
    cat > tests/unit/__init__.py << 'EOF'
# Unit tests package
EOF
    
    cat > tests/unit/test_log_event.py << 'EOF'
import pytest
from datetime import datetime
from src.models.log_event import LogEvent, LogLevel
from tests.factories.log_event_factory import LogEventFactory

class TestLogEvent:
    def test_log_event_creation(self):
        """Test basic log event creation."""
        event = LogEvent(
            message="Test message",
            level=LogLevel.INFO,
            source="test_app"
        )
        
        assert event.message == "Test message"
        assert event.level == LogLevel.INFO
        assert event.source == "test_app"
    
    def test_log_event_representation(self):
        """Test string representation of log event."""
        event = LogEvent(id=1, message="A" * 100, level=LogLevel.ERROR)
        repr_str = repr(event)
        
        assert "LogEvent(id=1" in repr_str
        assert "ERROR" in repr_str
        assert len(repr_str) < 150  # Should be truncated
    
    @pytest.mark.parametrize("level", [
        LogLevel.DEBUG,
        LogLevel.INFO,
        LogLevel.WARNING,
        LogLevel.ERROR,
        LogLevel.CRITICAL
    ])
    def test_all_log_levels(self, level):
        """Test all log levels are valid."""
        event = LogEvent(message="Test", level=level)
        assert event.level == level

class TestLogEventFactory:
    def test_create_single_log(self):
        """Test factory creates valid log event."""
        event = LogEventFactory.build()
        
        assert isinstance(event.message, str)
        assert event.level in LogLevel
        assert isinstance(event.timestamp, datetime)
    
    def test_create_batch(self):
        """Test factory creates multiple events."""
        events = LogEventFactory.build_batch(5)
        
        assert len(events) == 5
        assert all(isinstance(event.message, str) for event in events)
    
    def test_error_scenario_generation(self):
        """Test realistic error scenario generation."""
        logs = LogEventFactory.create_error_scenario(error_count=3, normal_count=5)
        
        assert len(logs) == 8
        
        # Check we have both normal and error logs
        levels = [log.level for log in logs]
        assert LogLevel.INFO in levels
        assert LogLevel.ERROR in levels
        
        # Error logs should have descriptive messages
        error_logs = [log for log in logs if log.level == LogLevel.ERROR]
        assert len(error_logs) == 3
        assert all("Database connection failed" in log.message for log in error_logs)
    
    def test_high_volume_simulation(self):
        """Test high-volume log generation."""
        logs = LogEventFactory.create_high_volume_simulation(
            events_per_minute=60, 
            duration_minutes=1
        )
        
        assert len(logs) == 60
        
        # Check timestamps are properly spaced
        timestamps = [log.timestamp for log in logs]
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                     for i in range(len(timestamps)-1)]
        
        # Should be approximately 1 second between events (60 events/minute)
        assert all(0.8 <= diff <= 1.2 for diff in time_diffs)
EOF
    
    # Create integration tests
    cat > tests/integration/__init__.py << 'EOF'
# Integration tests package
EOF
    
    cat > tests/integration/test_database.py << 'EOF'
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.log_event import LogEvent, LogLevel
from tests.factories.log_event_factory import LogEventFactory

@pytest.mark.integration
class TestLogEventDatabase:
    async def test_store_single_log_event(self, test_session: AsyncSession):
        """Test storing a single log event."""
        event = LogEvent(
            message="Integration test message",
            level=LogLevel.INFO,
            source="integration_test"
        )
        
        test_session.add(event)
        await test_session.commit()
        await test_session.refresh(event)
        
        assert event.id is not None
        assert event.message == "Integration test message"
    
    async def test_retrieve_log_events(self, test_session: AsyncSession):
        """Test retrieving log events from database."""
        # Create test events
        events = [
            LogEvent(message=f"Test {i}", level=LogLevel.INFO)
            for i in range(3)
        ]
        
        for event in events:
            test_session.add(event)
        await test_session.commit()
        
        # Retrieve events
        result = await test_session.execute(select(LogEvent))
        stored_events = result.scalars().all()
        
        assert len(stored_events) >= 3
        messages = [event.message for event in stored_events]
        assert "Test 0" in messages
        assert "Test 1" in messages
        assert "Test 2" in messages
    
    async def test_concurrent_log_storage(self, test_session: AsyncSession):
        """Test handling concurrent log writes."""
        async def store_log(session, message):
            event = LogEvent(message=message, level=LogLevel.INFO)
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event.id
        
        # Create multiple concurrent tasks
        tasks = [
            store_log(test_session, f"Concurrent log {i}")
            for i in range(5)
        ]
        
        # Execute concurrently
        event_ids = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all succeeded and got unique IDs
        assert len(event_ids) == 5
        assert all(isinstance(id_val, int) for id_val in event_ids)
        assert len(set(event_ids)) == 5  # All unique
    
    @pytest.mark.slow
    async def test_high_volume_log_processing(self, test_session: AsyncSession):
        """Test system behavior under high load."""
        import time
        
        # Generate realistic high-volume scenario
        events = LogEventFactory.create_high_volume_simulation(
            events_per_minute=100, 
            duration_minutes=1
        )
        
        start_time = time.time()
        
        for event in events:
            test_session.add(event)
        
        await test_session.commit()
        duration = time.time() - start_time
        
        # Verify performance and data integrity
        assert duration < 10  # Should process 100 logs quickly
        
        # Count stored events
        result = await test_session.execute(select(LogEvent))
        stored_count = len(result.scalars().all())
        assert stored_count >= 100
EOF
    
    # Create API module
    mkdir -p src/api
    cat > src/api/__init__.py << 'EOF'
# API package
EOF
    
    cat > src/api/main.py << 'EOF'
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.database import get_database_session
from src.models.log_event import LogEvent, LogLevel
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LogEventCreate(BaseModel):
    message: str
    level: LogLevel = LogLevel.INFO
    source: Optional[str] = None
    metadata: Optional[str] = None

class LogEventResponse(BaseModel):
    id: int
    message: str
    level: LogLevel
    timestamp: datetime
    source: Optional[str]
    metadata: Optional[str]
    
    class Config:
        from_attributes = True

def create_app() -> FastAPI:
    app = FastAPI(title="Log Processing System", version="1.0.0")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "log-processor"}
    
    @app.post("/logs", response_model=LogEventResponse)
    async def create_log_event(
        log_data: LogEventCreate,
        session: AsyncSession = Depends(get_database_session)
    ):
        """Create a new log event."""
        event = LogEvent(**log_data.dict())
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event
    
    @app.get("/logs", response_model=List[LogEventResponse])
    async def get_log_events(
        limit: int = 100,
        level: Optional[LogLevel] = None,
        session: AsyncSession = Depends(get_database_session)
    ):
        """Retrieve log events with optional filtering."""
        query = select(LogEvent).limit(limit).order_by(LogEvent.timestamp.desc())
        
        if level:
            query = query.where(LogEvent.level == level)
        
        result = await session.execute(query)
        return result.scalars().all()
    
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
    
    cd ..
    log_success "Backend testing framework setup complete"
}

setup_frontend_testing() {
    log_info "Setting up frontend testing framework..."
    
    cd frontend
    
    # Initialize package.json
    cat > package.json << 'EOF'
{
  "name": "log-processing-frontend",
  "version": "1.0.0",
  "description": "Frontend for distributed log processing system",
  "main": "src/index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "test:coverage": "react-scripts test --coverage --watchAll=false",
    "eject": "react-scripts eject"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "web-vitals": "^3.5.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.1",
    "jest": "^27.5.1",
    "msw": "^1.3.2"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
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
  },
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{js,jsx}",
      "!src/index.js",
      "!src/reportWebVitals.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 70,
        "functions": 70,
        "lines": 70,
        "statements": 70
      }
    }
  }
}
EOF
    
    # Install dependencies
    npm install
    
    # Create test setup
    cat > src/setupTests.js << 'EOF'
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock fetch globally
global.fetch = jest.fn();

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers that are declared in a test
afterEach(() => {
  server.resetHandlers();
  fetch.mockClear();
});

// Clean up after the tests are finished
afterAll(() => server.close());

// Global test utilities
export const mockApiResponse = (data, status = 200) => {
  fetch.mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
    text: async () => JSON.stringify(data),
  });
};

export const mockApiError = (status = 500, message = 'Server Error') => {
  fetch.mockRejectedValueOnce(new Error(message));
};

export const createMockLogEvent = (overrides = {}) => ({
  id: 1,
  message: 'Test log message',
  level: 'INFO',
  timestamp: new Date().toISOString(),
  source: 'test-app',
  metadata: null,
  ...overrides,
});

export const createMockLogEvents = (count = 5) => {
  return Array.from({ length: count }, (_, index) =>
    createMockLogEvent({
      id: index + 1,
      message: `Test log message ${index + 1}`,
    })
  );
};
EOF
    
    # Create mock server setup
    mkdir -p src/mocks
    cat > src/mocks/handlers.js << 'EOF'
import { rest } from 'msw';

export const handlers = [
  // Health check endpoint
  rest.get('/health', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({ status: 'healthy', service: 'log-processor' })
    );
  }),

  // Get log events
  rest.get('/logs', (req, res, ctx) => {
    const mockLogs = [
      {
        id: 1,
        message: 'Application started',
        level: 'INFO',
        timestamp: new Date().toISOString(),
        source: 'app',
        metadata: null,
      },
      {
        id: 2,
        message: 'Database connection established',
        level: 'INFO',
        timestamp: new Date().toISOString(),
        source: 'database',
        metadata: null,
      },
    ];

    return res(ctx.status(200), ctx.json(mockLogs));
  }),

  // Create log event
  rest.post('/logs', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        message: req.body.message,
        level: req.body.level || 'INFO',
        timestamp: new Date().toISOString(),
        source: req.body.source,
        metadata: req.body.metadata,
      })
    );
  }),
];
EOF
    
    cat > src/mocks/server.js << 'EOF'
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Setup requests interception using the given handlers
export const server = setupServer(...handlers);
EOF
    
    # Create main App component
    cat > src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newLog, setNewLog] = useState({
    message: '',
    level: 'INFO',
    source: '',
  });

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/logs`);
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      const data = await response.json();
      setLogs(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createLog = async (e) => {
    e.preventDefault();
    
    if (!newLog.message.trim()) {
      alert('Message is required');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLog),
      });

      if (!response.ok) {
        throw new Error('Failed to create log');
      }

      const createdLog = await response.json();
      setLogs([createdLog, ...logs]);
      setNewLog({ message: '', level: 'INFO', source: '' });
      
      // Show success message
      alert('Log created successfully');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const getLevelColor = (level) => {
    const colors = {
      DEBUG: '#6c757d',
      INFO: '#0dcaf0',
      WARNING: '#ffc107',
      ERROR: '#dc3545',
      CRITICAL: '#6f42c1',
    };
    return colors[level] || '#6c757d';
  };

  if (loading) {
    return <div className="loading">Loading logs...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Log Processing System</h1>
        <p>Distributed Systems Testing Framework - Day 6</p>
      </header>

      <main>
        <section className="log-form">
          <h2>Create New Log Event</h2>
          <form onSubmit={createLog}>
            <div className="form-group">
              <label htmlFor="message">Message:</label>
              <textarea
                id="message"
                value={newLog.message}
                onChange={(e) => setNewLog({ ...newLog, message: e.target.value })}
                placeholder="Enter log message..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="level">Level:</label>
              <select
                id="level"
                value={newLog.level}
                onChange={(e) => setNewLog({ ...newLog, level: e.target.value })}
              >
                <option value="DEBUG">Debug</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="ERROR">Error</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="source">Source:</label>
              <input
                type="text"
                id="source"
                value={newLog.source}
                onChange={(e) => setNewLog({ ...newLog, source: e.target.value })}
                placeholder="Application name or source..."
              />
            </div>

            <button type="submit">Create Log</button>
          </form>
        </section>

        <section className="logs-list">
          <h2>Recent Log Events ({logs.length})</h2>
          {logs.length === 0 ? (
            <p>No logs available</p>
          ) : (
            <div className="logs">
              {logs.map((log) => (
                <div key={log.id} className="log-item">
                  <div className="log-header">
                    <span
                      className="log-level"
                      style={{ backgroundColor: getLevelColor(log.level) }}
                    >
                      {log.level}
                    </span>
                    <span className="log-timestamp">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                    {log.source && (
                      <span className="log-source">({log.source})</span>
                    )}
                  </div>
                  <div className="log-message">{log.message}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
EOF
    
    # Create CSS
    cat > src/App.css << 'EOF'
.App {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.App-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 5px;
}

.log-form {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 10px;
  margin-bottom: 40px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

button {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s;
}

button:hover {
  background: #0056b3;
}

.logs-list h2 {
  color: #333;
  margin-bottom: 20px;
}

.logs {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.log-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.log-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.log-level {
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.log-timestamp {
  color: #6c757d;
  font-size: 14px;
}

.log-source {
  color: #495057;
  font-style: italic;
  font-size: 14px;
}

.log-message {
  color: #333;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .App {
    padding: 10px;
  }
  
  .log-form {
    padding: 20px;
  }
  
  .log-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
EOF
    
    # Create component tests
    cat > src/App.test.js << 'EOF'
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { mockApiResponse, createMockLogEvents } from './setupTests';

// Ensure fetch is mocked
global.fetch = jest.fn();

beforeEach(() => {
  global.fetch = jest.fn();
  fetch.mockClear();
});

// Mock fetch globally for these tests
beforeEach(() => {
  fetch.mockClear();
});

describe('App Component', () => {

  test('renders log processing system title', async () => {
  mockApiResponse([]); // Mock empty logs response
  render(<App />);
  
  // Wait for loading to complete and title to appear
  await waitFor(() => {
    expect(screen.getByText('Log Processing System')).toBeInTheDocument();
  });
    expect(screen.getByText(/Distributed Systems Testing Framework/)).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    mockApiResponse([], 200);
    render(<App />);
    
    expect(screen.getByText('Loading logs...')).toBeInTheDocument();
  });

  test('fetches and displays logs on mount', async () => {
    const mockLogs = createMockLogEvents(2);
    mockApiResponse(mockLogs);
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Test log message 1')).toBeInTheDocument();
      expect(screen.getByText('Test log message 2')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Recent Log Events (2)')).toBeInTheDocument();
  });

  test('handles log creation successfully', async () => {
    const user = userEvent.setup();
    const mockLogs = [];
    const newLog = {
      id: 3,
      message: 'New test log',
      level: 'WARNING',
      timestamp: new Date().toISOString(),
      source: 'test-app',
      metadata: null,
    };

    // Mock initial empty logs fetch
    mockApiResponse(mockLogs);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Recent Log Events (0)')).toBeInTheDocument();
    });

    // Mock successful log creation
    mockApiResponse(newLog, 201);

    // Fill out the form
    const messageInput = screen.getByLabelText(/message/i);
    const levelSelect = screen.getByLabelText(/level/i);
    const sourceInput = screen.getByLabelText(/source/i);
    const submitButton = screen.getByRole('button', { name: /create log/i });

    await user.type(messageInput, 'New test log');
    await user.selectOptions(levelSelect, 'WARNING');
    await user.type(sourceInput, 'test-app');
    await user.click(submitButton);

    // Verify the form submission
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/logs'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: 'New test log',
            level: 'WARNING',
            source: 'test-app',
          }),
        })
      );
    });
  });

  test('validates required message field', async () => {
    const user = userEvent.setup();
    
    // Mock empty logs response
    mockApiResponse([]);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Recent Log Events (0)')).toBeInTheDocument();
    });

    // Try to submit without message
    const submitButton = screen.getByRole('button', { name: /create log/i });
    
    // Mock window.alert
    window.alert = jest.fn();
    
    await user.click(submitButton);

    expect(window.alert).toHaveBeenCalledWith('Message is required');
  });

  test('handles API error gracefully', async () => {
    // Mock fetch to reject
    fetch.mockRejectedValueOnce(new Error('Network error'));
    
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/)).toBeInTheDocument();
    });
  });

  test('displays log levels with correct styling', async () => {
    const mockLogs = [
      {
        id: 1,
        message: 'Debug message',
        level: 'DEBUG',
        timestamp: new Date().toISOString(),
        source: 'app',
        metadata: null,
      },
      {
        id: 2,
        message: 'Error message',
        level: 'ERROR',
        timestamp: new Date().toISOString(),
        source: 'app',
        metadata: null,
      },
    ];

    mockApiResponse(mockLogs);
    render(<App />);

    await waitFor(() => {
      const debugLevel = screen.getByText('DEBUG');
      const errorLevel = screen.getByText('ERROR');
      
      expect(debugLevel).toBeInTheDocument();
      expect(errorLevel).toBeInTheDocument();
      
      // Check that levels have styling applied
      expect(debugLevel).toHaveStyle('background-color: #6c757d');
      expect(errorLevel).toHaveStyle('background-color: #dc3545');
    });
  });

  test('resets form after successful submission', async () => {
    const user = userEvent.setup();
    
    // Mock empty logs response
    mockApiResponse([]);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Recent Log Events (0)')).toBeInTheDocument();
    });

    // Mock successful creation
    mockApiResponse({
      id: 1,
      message: 'Test message',
      level: 'INFO',
      timestamp: new Date().toISOString(),
      source: 'test',
      metadata: null,
    }, 201);

    // Fill and submit form
    const messageInput = screen.getByLabelText(/message/i);
    const sourceInput = screen.getByLabelText(/source/i);
    
    await user.type(messageInput, 'Test message');
    await user.type(sourceInput, 'test');
    
    // Mock alert
    window.alert = jest.fn();
    
    await user.click(screen.getByRole('button', { name: /create log/i }));

    // Wait for form reset
    await waitFor(() => {
      expect(messageInput.value).toBe('');
      expect(sourceInput.value).toBe('');
    });
    
    expect(window.alert).toHaveBeenCalledWith('Log created successfully');
  });
});
EOF
    
    # Create index.js
    cat > src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF
    
    # Create index.css
    cat > src/index.css << 'EOF'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

* {
  box-sizing: border-box;
}
EOF
    
    # Create public/index.html
    mkdir -p public
    cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Log Processing System - Distributed Systems Testing Framework"
    />
    <title>Log Processing System</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF
    
    cd ..
    log_success "Frontend testing framework setup complete"
}

setup_docker_testing() {
    log_info "Setting up Docker testing environment..."
    
    mkdir -p config/docker
    
    # Create test docker-compose file
    cat > config/docker/docker-compose.test.yml << 'EOF'
version: '3.8'

services:
  test-postgres:
    image: postgres:15-alpine
    container_name: test-postgres-1
    environment:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: test_logs
    ports:
      - "5433:5432"
    volumes:
      - test_postgres_data:/var/lib/postgresql/data
      - ./init-test-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user -d test_logs"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - test-network

  test-redis:
    image: redis:7-alpine
    container_name: test-redis-1
    ports:
      - "6380:6379"
    command: redis-server --appendonly yes
    volumes:
      - test_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - test-network

volumes:
  test_postgres_data:
  test_redis_data:

networks:
  test-network:
    driver: bridge
EOF
    
    # Create database initialization script
    cat > config/docker/init-test-db.sql << 'EOF'
-- Test database initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create test schemas
CREATE SCHEMA IF NOT EXISTS logs;
CREATE SCHEMA IF NOT EXISTS metrics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA logs TO test_user;
GRANT ALL PRIVILEGES ON SCHEMA metrics TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA logs TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA metrics TO test_user;

-- Create test data function
CREATE OR REPLACE FUNCTION generate_test_data()
RETURNS void AS $$
BEGIN
    -- This function can be called to generate test data
    RAISE NOTICE 'Test database initialized successfully';
END;
$$ LANGUAGE plpgsql;

SELECT generate_test_data();
EOF
    
    log_success "Docker testing environment setup complete"
}

create_build_scripts() {
    log_info "Creating build and verification scripts..."
    
    # Create main build script
    cat > build_and_verify.sh << 'EOF'
#!/bin/bash

# Complete build and verification script
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_step() { echo -e "${BLUE}🔄 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🚀 Starting complete build and verification process..."

# Backend build and test
log_step "Setting up backend environment"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
log_success "Backend environment ready"

# Run backend tests
log_step "Running backend unit tests"
python -m pytest tests/unit/ -v --tb=short
log_success "Backend unit tests passed"

log_step "Running backend integration tests (requires Docker)"
if command -v docker &> /dev/null; then
    # Start test services
    docker-compose -f ../config/docker/docker-compose.test.yml up -d
    
    # Wait for services to be ready
    sleep 10
    
    # Set environment variables
    export POSTGRES_URL="postgresql+asyncpg://test_user:test_password@localhost:5433/test_logs"
    export REDIS_URL="redis://localhost:6380/0"
    
    # Run integration tests
    python -m pytest tests/integration/ -v --tb=short
    log_success "Backend integration tests passed"
    
    # Cleanup
    docker-compose -f ../config/docker/docker-compose.test.yml down
else
    log_error "Docker not available, skipping integration tests"
fi

cd ..

# Frontend build and test
log_step "Installing frontend dependencies"
cd frontend
npm install --silent
log_success "Frontend dependencies installed"

log_step "Running frontend tests"
npm test -- --watchAll=false --coverage
log_success "Frontend tests passed"

log_step "Building frontend"
npm run build
log_success "Frontend build completed"

cd ..

# Generate coverage reports
log_step "Generating coverage reports"
cd backend
source venv/bin/activate
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
log_success "Backend coverage report generated"

cd ../frontend
npm run test:coverage
log_success "Frontend coverage report generated"

cd ..

echo ""
echo "🎉 Build and verification completed successfully!"
echo ""
echo "📊 Coverage Reports:"
echo "   Backend:  ./backend/htmlcov/index.html"
echo "   Frontend: ./frontend/coverage/lcov-report/index.html"
echo ""
echo "🚀 Ready for development!"
EOF
    
    chmod +x build_and_verify.sh
    
    # Create demo script
    cat > demo.sh << 'EOF'
#!/bin/bash

# Demo script to showcase the testing framework
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🎬 Testing Framework Demo${NC}"
echo "========================="

echo -e "${YELLOW}1️⃣  Running backend unit tests...${NC}"
cd backend
source venv/bin/activate
python -m pytest tests/unit/test_log_event.py::TestLogEvent::test_log_event_creation -v
python -m pytest tests/unit/test_log_event.py::TestLogEventFactory::test_create_single_log -v
python -m pytest tests/unit/test_log_event.py::TestLogEventFactory::test_error_scenario_generation -v
echo -e "${GREEN}✅ Backend unit tests passed${NC}"

echo ""
echo -e "${YELLOW}2️⃣  Testing data factories...${NC}"
python -c "
from tests.factories.log_event_factory import LogEventFactory
from src.models.log_event import LogLevel

# Test single log creation
log = LogEventFactory.build()
print(f'✅ Created log: {log.level} - {log.message[:50]}...')

# Test batch creation
logs = LogEventFactory.build_batch(3)
print(f'✅ Created batch of {len(logs)} logs')

# Test error scenario
error_logs = LogEventFactory.create_error_scenario(error_count=2, normal_count=3)
print(f'✅ Created error scenario with {len(error_logs)} logs')
"

echo ""
echo -e "${YELLOW}3️⃣  Testing frontend components...${NC}"
cd ../frontend
npm test -- --testNamePattern="renders log processing system title" --watchAll=false --silent
echo -e "${GREEN}✅ Frontend component tests passed${NC}"

echo ""
echo -e "${YELLOW}4️⃣  Testing user interactions...${NC}"
npm test -- --testNamePattern="handles log creation" --watchAll=false --silent
echo -e "${GREEN}✅ User interaction tests passed${NC}"

echo ""
echo -e "${GREEN}🎉 Demo completed! Your testing framework is working correctly.${NC}"
echo ""
echo "Next steps:"
echo "• Run 'npm start' in frontend/ to see the UI"
echo "• Run './build_and_verify.sh' for full test suite"
echo "• Check coverage reports after running tests"
EOF
    
    chmod +x demo.sh
    
    log_success "Build scripts created"
}

run_verification() {
    log_info "Running initial verification..."
    
    # Quick backend test
    cd backend
    source venv/bin/activate
    python -c "
import pytest
from tests.factories.log_event_factory import LogEventFactory
from src.models.log_event import LogEvent, LogLevel

# Test factory
log = LogEventFactory.build()
assert isinstance(log.message, str)
assert log.level in LogLevel
print('✅ Backend factory test passed')

# Test model
event = LogEvent(message='Test', level=LogLevel.INFO)
assert event.message == 'Test'
print('✅ Backend model test passed')
"
    cd ..
    
    # Quick frontend test
    cd frontend
    npm test -- --testNamePattern="renders" --watchAll=false --silent > /dev/null 2>&1
    echo "✅ Frontend test passed"
    cd ..
    
    log_success "Initial verification completed"
}

# Main execution
main() {
    echo "🚀 Starting Testing Framework Setup - Day 6"
    echo "============================================="
    
    check_prerequisites
    create_project_structure
    setup_backend_testing
    setup_frontend_testing
    setup_docker_testing
    create_build_scripts
    run_verification
    
    echo ""
    echo "🎉 Testing Framework Setup Complete!"
    echo ""
    echo "📁 Project Structure:"
    echo "   backend/     - Python testing framework with pytest"
    echo "   frontend/    - React testing with Jest & Testing Library"
    echo "   config/      - Docker testing environment"
    echo "   docs/        - Documentation"
    echo ""
    echo "🚀 Quick Start:"
    echo "   ./demo.sh           - Run demonstration"
    echo "   ./build_and_verify.sh - Complete build and test"
    echo ""
    echo "📊 View Results:"
    echo "   cd backend && source venv/bin/activate && python -m pytest tests/ --cov=src --cov-report=html"
    echo "   cd frontend && npm run test:coverage"
    echo ""
    echo "Ready for Day 7: End-to-End Integration! 🎯"
}

# Run main function
main "$@"
EOF

chmod +x implementation_script
log_success "Complete implementation script created"