#!/bin/bash

# InfraWatch Backend Setup & Testing Script
# This script demonstrates infrastructure automation principles used in production systems
# Similar to how Netflix or Spotify automate their deployment pipelines

set -e  # Exit on any error - critical for production scripts

# Color codes for better user experience (UX principle in tooling)
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions - essential for debugging distributed systems
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists (defensive programming)
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for user confirmation (interactive learning)
wait_for_user() {
    echo -e "\n${YELLOW}Press Enter to continue to the next step...${NC}"
    read -r
}

# Function to check if port is available (important for service orchestration)
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        log_warning "Port $port is already in use. Please stop the service using this port."
        return 1
    fi
    return 0
}

# Function to test API endpoints (automated testing principle)
test_endpoint() {
    local url=$1
    local description=$2
    local max_retries=10
    local retry_count=0
    
    log_info "Testing $description..."
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_success "$description is responding"
            curl -s "$url" | python3 -m json.tool 2>/dev/null || curl -s "$url"
            echo ""
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_info "Retry $retry_count/$max_retries for $description..."
        sleep 2
    done
    
    log_error "$description failed to respond after $max_retries attempts"
    return 1
}

# Function to cleanup processes (resource management)
cleanup() {
    log_info "Cleaning up processes..."
    pkill -f "python run.py" 2>/dev/null || true
    pkill -f "gunicorn" 2>/dev/null || true
    docker-compose down 2>/dev/null || true
}

# Trap to ensure cleanup on script exit (proper resource management)
trap cleanup EXIT

echo "=================================================================="
echo "🚀 InfraWatch Backend Setup & Testing Script"
echo "=================================================================="
echo "This script will:"
echo "1. Create the complete project structure"
echo "2. Set up Python virtual environment"
echo "3. Install dependencies"
echo "4. Create all source files"
echo "5. Test locally without Docker"
echo "6. Test with Docker containers"
echo "7. Verify all endpoints are working"
echo ""
echo "This demonstrates production deployment automation used by major tech companies."
echo "=================================================================="
wait_for_user

# Step 1: Project Structure Creation
log_info "Step 1: Creating InfraWatch project structure..."

# Navigate to the existing repository (assuming it exists from Day 1)
if [ ! -d "InfraWatch" ]; then
    log_info "InfraWatch repository not found. Creating it now..."
    mkdir InfraWatch
    cd InfraWatch
    git init
    log_success "Created InfraWatch repository"
else
    cd InfraWatch
    log_success "Found existing InfraWatch repository"
fi

# Create comprehensive directory structure
log_info "Creating backend directory structure..."
mkdir -p backend/{app/{api/v1,core,models,services,static,templates},tests/{unit,integration},config}

# Create all necessary files
log_info "Creating project files..."
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/core/{__init__.py,config.py,database.py}
touch backend/app/models/{__init__.py,infrastructure.py}
touch backend/app/services/{__init__.py,monitoring.py}
touch backend/{requirements.txt,requirements-dev.txt,Dockerfile,docker-compose.yml}
touch backend/{run.py,.env.example,.env}
touch backend/tests/__init__.py

log_success "Project structure created successfully"
wait_for_user

# Step 2: Create source files with content
log_info "Step 2: Creating source files with production-ready code..."

# Create main application factory
cat > backend/app/__init__.py << 'EOF'
from flask import Flask
from app.core.config import Config
from app.api.v1 import health_bp, infrastructure_bp

def create_app(config_class=Config):
    """Application factory pattern - enables testing and multiple configurations"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints (modular architecture)
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(infrastructure_bp, url_prefix='/api/v1')
    
    return app
EOF

# Create configuration management
cat > backend/app/core/config.py << 'EOF'
import os
from datetime import timedelta

class Config:
    """Production-ready configuration management"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///infrawatch.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Production performance settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # API versioning and rate limiting
    API_VERSION = 'v1'
    RATE_LIMIT_ENABLED = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
EOF

# Create infrastructure models
cat > backend/app/models/infrastructure.py << 'EOF'
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Server:
    """Represents a monitored server in our infrastructure"""
    id: str
    hostname: str
    ip_address: str
    status: str  # 'healthy', 'warning', 'critical'
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    last_heartbeat: datetime
    
    def to_dict(self) -> Dict:
        """Serialize for API responses"""
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'status': self.status,
            'metrics': {
                'cpu_usage': self.cpu_usage,
                'memory_usage': self.memory_usage,
                'disk_usage': self.disk_usage
            },
            'last_heartbeat': self.last_heartbeat.isoformat()
        }

@dataclass
class InfrastructureCluster:
    """Represents a cluster of servers (like a Kubernetes cluster)"""
    name: str
    servers: List[Server]
    
    @property
    def healthy_servers(self) -> int:
        return len([s for s in self.servers if s.status == 'healthy'])
    
    @property
    def total_servers(self) -> int:
        return len(self.servers)
EOF

# Create API blueprints
cat > backend/app/api/v1/__init__.py << 'EOF'
from flask import Blueprint, jsonify, request
from app.models.infrastructure import Server, InfrastructureCluster
from datetime import datetime, timedelta
import random

health_bp = Blueprint('health', __name__)
infrastructure_bp = Blueprint('infrastructure', __name__)

@health_bp.route('/health')
def health_check():
    """Health endpoint - critical for load balancers and monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'service': 'infrawatch-backend'
    })

@infrastructure_bp.route('/servers')
def get_servers():
    """Get all monitored servers - simulates real infrastructure data"""
    # In production, this would query your database
    mock_servers = [
        Server(
            id=f'server-{i}',
            hostname=f'web-{i}.example.com',
            ip_address=f'10.0.1.{i+10}',
            status=random.choice(['healthy', 'warning', 'critical']),
            cpu_usage=random.uniform(10, 90),
            memory_usage=random.uniform(20, 80),
            disk_usage=random.uniform(30, 70),
            last_heartbeat=datetime.utcnow() - timedelta(seconds=random.randint(0, 300))
        ) for i in range(5)
    ]
    
    return jsonify({
        'servers': [server.to_dict() for server in mock_servers],
        'total_count': len(mock_servers),
        'timestamp': datetime.utcnow().isoformat()
    })

@infrastructure_bp.route('/clusters')
def get_clusters():
    """Get infrastructure clusters overview"""
    # Simulate cluster data
    servers = [
        Server(f'node-{i}', f'k8s-node-{i}', f'10.0.2.{i+10}', 
               'healthy', 45.2, 60.1, 35.8, datetime.utcnow())
        for i in range(3)
    ]
    
    cluster = InfrastructureCluster('production-cluster', servers)
    
    return jsonify({
        'cluster_name': cluster.name,
        'total_servers': cluster.total_servers,
        'healthy_servers': cluster.healthy_servers,
        'servers': [server.to_dict() for server in cluster.servers]
    })
EOF

# Create application entry point
cat > backend/run.py << 'EOF'
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Development server - never use in production
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

# Create requirements files
cat > backend/requirements.txt << 'EOF'
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
python-dotenv==1.0.0
gunicorn==21.2.0
EOF

cat > backend/requirements-dev.txt << 'EOF'
-r requirements.txt
pytest==7.4.2
pytest-cov==4.1.0
black==23.7.0
flake8==6.0.0
EOF

# Create environment files
cat > backend/.env.example << 'EOF'
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///infrawatch.db
FLASK_ENV=development
FLASK_DEBUG=1
EOF

cp backend/.env.example backend/.env

# Create Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user (security best practice)
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
EOF

# Create Docker Compose
cat > backend/docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=sqlite:///infrawatch.db
    volumes:
      - .:/app
    command: python run.py
EOF

log_success "All source files created successfully"
wait_for_user

# Step 3: Python Environment Setup
log_info "Step 3: Setting up Python virtual environment..."

cd backend

# Check if Python 3.11+ is available
if ! command_exists python3; then
    log_error "Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
log_info "Using Python version: $python_version"

# Create virtual environment
log_info "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
log_info "Installing production dependencies..."
pip install -r requirements.txt

log_info "Installing development dependencies..."
pip install -r requirements-dev.txt

log_success "Python environment setup completed"
wait_for_user

# Step 4: Local Testing (Without Docker)
log_info "Step 4: Testing application locally (without Docker)..."

# Check if port 5000 is available
if ! check_port 5000; then
    log_error "Port 5000 is not available. Please stop any service using this port."
    exit 1
fi

log_info "Starting Flask development server..."
python run.py &
FLASK_PID=$!

# Wait for server to start
log_info "Waiting for server to start..."
sleep 5

# Test all endpoints
log_info "Testing API endpoints..."
echo ""

test_endpoint "http://localhost:5000/api/v1/health" "Health Check Endpoint"
echo ""
test_endpoint "http://localhost:5000/api/v1/servers" "Servers Endpoint"
echo ""
test_endpoint "http://localhost:5000/api/v1/clusters" "Clusters Endpoint"

# Stop the Flask server
log_info "Stopping Flask development server..."
kill $FLASK_PID 2>/dev/null || true
sleep 2

log_success "Local testing completed successfully"
wait_for_user

# Step 5: Docker Testing
log_info "Step 5: Testing with Docker containers..."

# Check if Docker is installed
if ! command_exists docker; then
    log_error "Docker is not installed. Please install Docker to continue."
    log_info "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    log_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Determine compose command
COMPOSE_CMD="docker-compose"
if ! command_exists docker-compose; then
    COMPOSE_CMD="docker compose"
fi

log_info "Building Docker image..."
docker build -t infrawatch-backend .

log_info "Starting application with Docker Compose..."
$COMPOSE_CMD up -d --build

# Wait for container to be ready
log_info "Waiting for Docker container to start..."
sleep 10

# Test endpoints with Docker
log_info "Testing API endpoints via Docker..."
echo ""

test_endpoint "http://localhost:5000/api/v1/health" "Health Check Endpoint (Docker)"
echo ""
test_endpoint "http://localhost:5000/api/v1/servers" "Servers Endpoint (Docker)"
echo ""
test_endpoint "http://localhost:5000/api/v1/clusters" "Clusters Endpoint (Docker)"

# Show container logs
log_info "Application logs from Docker container:"
$COMPOSE_CMD logs backend

# Stop Docker services
log_info "Stopping Docker services..."
$COMPOSE_CMD down

log_success "Docker testing completed successfully"
wait_for_user

# Step 6: Verification Summary
echo ""
echo "=================================================================="
log_success "🎉 InfraWatch Backend Setup & Testing COMPLETED!"
echo "=================================================================="
echo ""
echo "✅ Project structure created"
echo "✅ Python virtual environment configured"
echo "✅ Dependencies installed"
echo "✅ Source files created with production patterns"
echo "✅ Local testing passed"
echo "✅ Docker containerization working"
echo "✅ All API endpoints responding correctly"
echo ""
echo "🚀 Your InfraWatch backend is ready for development!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source backend/venv/bin/activate"
echo "2. Start development server: cd backend && python run.py"
echo "3. Access APIs at: http://localhost:5000/api/v1/"
echo "4. Or use Docker: cd backend && docker-compose up"
echo ""
echo "Available endpoints:"
echo "• http://localhost:5000/api/v1/health"
echo "• http://localhost:5000/api/v1/servers"
echo "• http://localhost:5000/api/v1/clusters"
echo ""
echo "=================================================================="

# Optional: Open browser to health endpoint
if command_exists open; then
    echo "Opening health endpoint in browser..."
    # Start server quickly for demo
    cd backend
    source venv/bin/activate
    python run.py &
    sleep 3
    open "http://localhost:5000/api/v1/health"
    sleep 3
    pkill -f "python run.py" || true
elif command_exists xdg-open; then
    echo "Opening health endpoint in browser..."
    cd backend
    source venv/bin/activate
    python run.py &
    sleep 3
    xdg-open "http://localhost:5000/api/v1/health"
    sleep 3
    pkill -f "python run.py" || true
fi

log_success "Setup script completed successfully! 🚀"