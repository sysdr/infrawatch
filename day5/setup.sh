#!/bin/bash

# Day 5: Database & Containerization - Implementation Script
# Full setup, build, test, and verification automation

set -e  # Exit on any error

echo "=== Day 5: Database & Containerization Setup ==="
echo "Setting up PostgreSQL with Docker Compose and Redis caching..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check for Python 3.11
    if ! command -v python3.11 &> /dev/null; then
        print_error "Python 3.11 is not installed. Please install Python 3.11 first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create project structure
create_project_structure() {
    print_status "Creating project structure..."
    
    # Main project directory
    mkdir -p distributed-systems-day5
    cd distributed-systems-day5
    
    # Database related directories
    mkdir -p {database/{migrations,seeds,scripts},docker,config,src/{models,repositories,services},tests/{unit,integration},logs}
    
    print_success "Project structure created"
}

# Create Docker Compose configuration
create_docker_compose() {
    print_status "Creating Docker Compose configuration..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: log_processor_db
    environment:
      POSTGRES_DB: log_processor
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d/migrations
      - ./database/seeds:/docker-entrypoint-initdb.d/seeds
    networks:
      - log_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devuser -d log_processor"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: log_processor_cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - log_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  adminer:
    image: adminer:4.8.1
    container_name: log_processor_admin
    ports:
      - "8080:8080"
    networks:
      - log_network
    depends_on:
      - postgres

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  log_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF

    print_success "Docker Compose configuration created"
}

# Create database initialization scripts
create_database_scripts() {
    print_status "Creating database initialization scripts..."
    
    # Migration script
    cat > database/migrations/001_create_tables.sql << 'EOF'
-- Log Processing System Database Schema
-- Migration 001: Create core tables

-- Drop existing objects if they exist
DROP TABLE IF EXISTS users, log_sources, log_entries, log_metrics CASCADE;
DROP VIEW IF EXISTS log_entries_recent, error_summary;
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_log_sources_updated_at ON log_sources;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Log sources configuration
CREATE TABLE log_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'file', 'api', 'stream'
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Raw log entries
CREATE TABLE log_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES log_sources(id),
    raw_message TEXT NOT NULL,
    parsed_data JSONB,
    severity_level VARCHAR(20) DEFAULT 'INFO',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Processed metrics for analytics
CREATE TABLE log_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES log_sources(id),
    metric_type VARCHAR(50) NOT NULL,
    metric_value NUMERIC NOT NULL,
    dimensions JSONB,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_log_entries_source_id ON log_entries(source_id);
CREATE INDEX idx_log_entries_severity ON log_entries(severity_level);
CREATE INDEX idx_log_entries_timestamp ON log_entries(timestamp DESC);
CREATE INDEX idx_log_entries_source_timestamp ON log_entries(source_id, timestamp DESC);
CREATE INDEX idx_log_metrics_source_type ON log_metrics(source_id, metric_type);
CREATE INDEX idx_log_metrics_calculated_at ON log_metrics(calculated_at);

-- Create trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_log_sources_updated_at BEFORE UPDATE ON log_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE log_entries IS 'Stores raw and processed log entries from various sources';
COMMENT ON TABLE log_sources IS 'Configuration for different log input sources';
COMMENT ON TABLE log_metrics IS 'Aggregated metrics calculated from log data';

-- Create views for common queries
CREATE VIEW log_entries_recent AS
SELECT
    le.id,
    ls.name as source_name,
    le.raw_message,
    le.severity_level,
    le.timestamp,
    le.parsed_data
FROM log_entries le
JOIN log_sources ls ON le.source_id = ls.id
WHERE le.timestamp >= CURRENT_TIMESTAMP - interval '24 hours'
ORDER BY le.timestamp DESC;

CREATE VIEW error_summary AS
SELECT
    ls.name as source_name,
    COUNT(*) as error_count,
    MAX(le.timestamp) as last_error
FROM log_entries le
JOIN log_sources ls ON le.source_id = ls.id
WHERE le.severity_level = 'ERROR'
    AND le.timestamp >= CURRENT_TIMESTAMP - interval '24 hours'
GROUP BY ls.name
ORDER BY error_count DESC;

EOF

    # Seed data script
    cat > database/seeds/002_seed_data.sql << 'EOF'
-- Seed data for development environment
-- Run after migrations

-- Create test users
INSERT INTO users (username, email, password_hash) VALUES
    ('admin', 'admin@logprocessor.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8QP5rq8Y3m'), -- password: admin123
    ('developer', 'dev@logprocessor.local', '$2b$12$EixZHVyRjKuFjk1Ql8UUCO8TZUHcZAVZ3nLKI5O0r5B4.w5i4Kq.m'), -- password: dev123
    ('viewer', 'viewer@logprocessor.local', '$2b$12$P3ybp1Df5yf/8jgL0dX3cuZV.J4j5vQjGJ8J3z4O2t1Nf9sL7p2gm'); -- password: view123

-- Create sample log sources
INSERT INTO log_sources (name, source_type, configuration) VALUES
    ('Web Server Access Logs', 'file', '{"path": "/var/log/nginx/access.log", "format": "combined"}'),
    ('Application API Logs', 'api', '{"endpoint": "http://app-server:8000/logs", "auth_token": "secret"}'),
    ('Database Query Logs', 'file', '{"path": "/var/log/postgresql/query.log", "format": "postgresql"}'),
    ('Error Monitoring Stream', 'stream', '{"topic": "errors", "bootstrap_servers": "kafka:9092"}');

-- Insert sample log entries
INSERT INTO log_entries (source_id, raw_message, parsed_data, severity_level, timestamp) 
SELECT 
    ls.id,
    'Sample log message #' || generate_series,
    jsonb_build_object(
        'ip', '192.168.1.' || (random() * 254)::int,
        'method', (ARRAY['GET', 'POST', 'PUT', 'DELETE'])[floor(random() * 4 + 1)],
        'status_code', (ARRAY[200, 201, 400, 404, 500])[floor(random() * 5 + 1)],
        'response_time', (random() * 1000)::int
    ),
    (ARRAY['DEBUG', 'INFO', 'WARN', 'ERROR'])[floor(random() * 4 + 1)],
    CURRENT_TIMESTAMP - (random() * interval '30 days')
FROM 
    log_sources ls,
    generate_series(1, 100);

-- Insert sample metrics
INSERT INTO log_metrics (source_id, metric_type, metric_value, dimensions)
SELECT 
    ls.id,
    'request_count',
    (random() * 1000)::int,
    jsonb_build_object('hour', extract(hour from CURRENT_TIMESTAMP), 'status', '2xx')
FROM log_sources ls;

-- Update statistics
ANALYZE users;
ANALYZE log_sources;
ANALYZE log_entries;
ANALYZE log_metrics;

-- Create views for common queries
CREATE VIEW log_entries_recent AS
SELECT 
    le.id,
    ls.name as source_name,
    le.raw_message,
    le.severity_level,
    le.timestamp,
    le.parsed_data
FROM log_entries le
JOIN log_sources ls ON le.source_id = ls.id
WHERE le.timestamp >= CURRENT_TIMESTAMP - interval '24 hours'
ORDER BY le.timestamp DESC;

CREATE VIEW error_summary AS
SELECT 
    ls.name as source_name,
    COUNT(*) as error_count,
    MAX(le.timestamp) as last_error
FROM log_entries le
JOIN log_sources ls ON le.source_id = ls.id
WHERE le.severity_level = 'ERROR'
    AND le.timestamp >= CURRENT_TIMESTAMP - interval '24 hours'
GROUP BY ls.name
ORDER BY error_count DESC;
EOF

    print_success "Database scripts created"
}

# Create Redis configuration
create_redis_config() {
    print_status "Creating Redis configuration..."
    
    cat > config/redis.conf << 'EOF'
# Redis configuration for log processing system
bind 0.0.0.0
port 6379

# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile ""

# Security
# requirepass yourpassword

# Performance
tcp-keepalive 300
tcp-backlog 511

# Append only file
appendonly yes
appendfsync everysec

# Key expiration
notify-keyspace-events Ex
EOF

    print_success "Redis configuration created"
}

# Create Python application code
create_application_code() {
    print_status "Creating application code..."
    
    # Database models
    cat > src/models/database.py << 'EOF'
"""Database models and connection management."""
import os
import asyncpg
import redis.asyncio as redis
from typing import Optional, Dict, Any
import json
from datetime import datetime
import uuid

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
    
    async def initialize(self):
        """Initialize database connections."""
        # PostgreSQL connection
        self.pg_pool = await asyncpg.create_pool(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            user=os.getenv('POSTGRES_USER', 'devuser'),
            password=os.getenv('POSTGRES_PASSWORD', 'devpass'),
            database=os.getenv('POSTGRES_DB', 'log_processor'),
            min_size=10,
            max_size=20
        )
        
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        
        print("Database connections initialized")
    
    async def close(self):
        """Close database connections."""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            await self.redis_client.close()

class LogEntry:
    """Log entry model."""
    
    def __init__(self, raw_message: str, source_id: str, 
                 severity_level: str = 'INFO', parsed_data: Dict = None):
        self.id = str(uuid.uuid4())
        self.raw_message = raw_message
        self.source_id = source_id
        self.severity_level = severity_level
        self.parsed_data = parsed_data or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'raw_message': self.raw_message,
            'source_id': self.source_id,
            'severity_level': self.severity_level,
            'parsed_data': self.parsed_data,
            'timestamp': self.timestamp.isoformat()
        }
EOF

    # Repository layer
    cat > src/repositories/log_repository.py << 'EOF'
"""Log repository for database operations."""
import asyncpg
import redis.asyncio as redis
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

class LogRepository:
    """Repository for log-related database operations."""
    
    def __init__(self, pg_pool: asyncpg.Pool, redis_client: redis.Redis):
        self.pg_pool = pg_pool
        self.redis = redis_client
    
    async def save_log_entry(self, log_entry: Dict[str, Any]) -> str:
        """Save a log entry to PostgreSQL."""
        async with self.pg_pool.acquire() as conn:
            query = """
                INSERT INTO log_entries (raw_message, source_id, severity_level, 
                                       timestamp, parsed_data)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """
            result = await conn.fetchval(
                query,
                log_entry['raw_message'],
                log_entry['source_id'],
                log_entry['severity_level'],
                datetime.fromisoformat(log_entry['timestamp']),
                json.dumps(log_entry['parsed_data'])
            )
            return str(result)
    
    async def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries with caching."""
        cache_key = f"recent_logs:{limit}"
        
        # Try cache first
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Query database
        async with self.pg_pool.acquire() as conn:
            query = """
                SELECT id, raw_message, severity_level, timestamp, parsed_data
                FROM log_entries_recent
                LIMIT $1
            """
            rows = await conn.fetch(query, limit)
            
            logs = []
            for row in rows:
                logs.append({
                    'id': str(row['id']),
                    'raw_message': row['raw_message'],
                    'severity_level': row['severity_level'],
                    'timestamp': row['timestamp'].isoformat(),
                    'parsed_data': json.loads(row['parsed_data'] or '{}')
                })
        
        # Cache results for 60 seconds
        await self.redis.setex(cache_key, 60, json.dumps(logs))
        return logs
    
    async def get_error_summary(self) -> List[Dict[str, Any]]:
        """Get error summary with caching."""
        cache_key = "error_summary"
        
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        async with self.pg_pool.acquire() as conn:
            query = "SELECT * FROM error_summary"
            rows = await conn.fetch(query)
            
            summary = []
            for row in rows:
                summary.append({
                    'source_name': row['source_name'],
                    'error_count': row['error_count'],
                    'last_error': row['last_error'].isoformat()
                })
        
        await self.redis.setex(cache_key, 300, json.dumps(summary))
        return summary
EOF

    # Test files
    cat > tests/test_database.py << 'EOF'
"""Test database functionality."""
import pytest
import pytest_asyncio
import asyncio
import asyncpg
import redis.asyncio as redis
import uuid
import json
from src.models.database import DatabaseManager, LogEntry
from src.repositories.log_repository import LogRepository

@pytest_asyncio.fixture
async def db_manager():
    """Create database manager for testing."""
    manager = DatabaseManager()
    await manager.initialize()
    try:
        yield manager
    finally:
        await manager.close()

@pytest.mark.asyncio
async def test_database_connection(db_manager):
    """Test database connections."""
    assert db_manager.pg_pool is not None
    assert db_manager.redis_client is not None

    # Test PostgreSQL
    async with db_manager.pg_pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
        assert result == 1

    # Test Redis
    await db_manager.redis_client.set("test_key", "test_value")
    value = await db_manager.redis_client.get("test_key")
    assert value == "test_value"

@pytest.mark.asyncio
async def test_log_repository(db_manager):
    """Test log repository operations."""
    repo = LogRepository(db_manager.pg_pool, db_manager.redis_client)

    # Create a test source first
    async with db_manager.pg_pool.acquire() as conn:
        source_id = await conn.fetchval(
            """
            INSERT INTO log_sources (name, source_type, configuration)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            "Test Source",
            "test",
            json.dumps({"test": "config"})
        )

    # Create test log entry
    log_entry = LogEntry(
        "Test log message",
        str(source_id),
        "INFO"
    )

    # Save to database
    log_id = await repo.save_log_entry(log_entry.to_dict())
    assert log_id is not None

    # Retrieve recent logs
    logs = await repo.get_recent_logs(limit=10)
    assert len(logs) > 0
    assert any(log['raw_message'] == "Test log message" for log in logs)
EOF

    print_success "Application code created"
}

# Create requirements file
create_requirements() {
    print_status "Creating requirements.txt..."
    
    cat > requirements.txt << 'EOF'
# Database & Caching
asyncpg==0.29.0
redis==5.0.1

# Web Framework
fastapi==0.104.1
uvicorn==0.24.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1

# Utilities
python-decouple==3.8
pydantic==2.5.0
EOF

    print_success "Requirements file created"
}

# Build and start services
build_and_start() {
    print_status "Building and starting services..."
    
    # Start services
    docker-compose up -d
    
    print_status "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    if docker-compose ps | grep -q "healthy"; then
        print_success "All services are healthy"
    else
        print_warning "Some services may not be fully ready yet"
        # Exit if services are not healthy after waiting
        exit 1
    fi

    print_status "Applying database migrations..."
    docker-compose exec -T postgres psql -U devuser -d log_processor < database/migrations/001_create_tables.sql
    
    print_status "Applying database seed data..."
    docker-compose exec -T postgres psql -U devuser -d log_processor < database/seeds/002_seed_data.sql

    print_success "Services built, started, and database initialized"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Remove any existing venv to ensure a clean environment
    rm -rf venv
    
    # Install Python dependencies in virtual environment using Python 3.11
    python3.11 -m venv venv
    source venv/bin/activate || . venv/Scripts/activate
    ./venv/bin/python -m pip install --upgrade pip
    ./venv/bin/python -m pip install -r requirements.txt
    
    # Set environment variables for testing
    export POSTGRES_HOST=localhost
    export POSTGRES_PORT=5432
    export POSTGRES_USER=devuser
    export POSTGRES_PASSWORD=devpass
    export POSTGRES_DB=log_processor
    export REDIS_HOST=localhost
    export REDIS_PORT=6379
    
    # Run tests
    ./venv/bin/python -m pytest tests/ -v
    
    deactivate 2>/dev/null || true
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    echo "=== Service Status ==="
    docker-compose ps
    
    echo -e "\n=== PostgreSQL Connection Test ==="
    docker-compose exec -T postgres psql -U devuser -d log_processor -c "SELECT COUNT(*) as log_entries FROM log_entries;"
    
    echo -e "\n=== Redis Connection Test ==="
    docker-compose exec -T redis redis-cli ping
    
    echo -e "\n=== Database Schema Verification ==="
    docker-compose exec -T postgres psql -U devuser -d log_processor -c "\dt"
    
    echo -e "\n=== Sample Data Verification ==="
    docker-compose exec -T postgres psql -U devuser -d log_processor -c "SELECT source_name, severity_level, COUNT(*) FROM log_entries_recent GROUP BY source_name, severity_level;"
    
    print_success "Verification completed"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    docker-compose down -v
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "Starting Day 5: Database & Containerization Implementation"
    echo "========================================================"
    
    check_prerequisites
    create_project_structure
    create_docker_compose
    create_database_scripts
    create_redis_config
    create_application_code
    create_requirements
    
    build_and_start
    
    echo -e "\n${GREEN}=== DEPLOYMENT SUMMARY ===${NC}"
    echo "✅ PostgreSQL running on port 5432"
    echo "✅ Redis running on port 6379"
    echo "✅ Adminer (DB admin) running on port 8080"
    echo "✅ Database initialized with sample data"
    echo "✅ Container networking configured"
    
    # Run tests
    run_tests
    
    # Verify deployment
    verify_deployment
    
    echo -e "\n${GREEN}=== ACCESS INFORMATION ===${NC}"
    echo "🔗 Database Admin UI: http://localhost:8080"
    echo "   - Server: postgres"
    echo "   - Username: devuser" 
    echo "   - Password: devpass"
    echo "   - Database: log_processor"
    echo ""
    echo "🔗 PostgreSQL Direct Connection:"
    echo "   - Host: localhost:5432"
    echo "   - Database: log_processor"
    echo "   - Username: devuser"
    echo "   - Password: devpass"
    echo ""
    echo "🔗 Redis Connection:"
    echo "   - Host: localhost:6379"
    echo "   - No password required"
    
    echo -e "\n${BLUE}=== NEXT STEPS ===${NC}"
    echo "1. Open http://localhost:8080 to explore the database"
    echo "2. Run 'docker-compose logs -f' to monitor service logs"
    echo "3. Execute 'docker-compose exec postgres psql -U devuser -d log_processor' for direct DB access"
    echo "4. Test Redis with 'docker-compose exec redis redis-cli'"
    echo "5. Run assignment: implement multi-environment setup"
    
    # Trap cleanup on script exit
    trap cleanup EXIT
    
    print_success "Implementation completed successfully!"
    print_warning "Press Ctrl+C to stop services and cleanup"
    
    # Keep script running
    while true; do
        sleep 30
        if ! docker-compose ps | grep -q "Up"; then
            print_error "Some services have stopped"
            break
        fi
    done
}

# Execute main function
main "$@"