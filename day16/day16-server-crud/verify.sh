#!/bin/bash

# Day 16: Server CRUD Operations - Verification Script
# This script verifies that all components are working correctly

set -e

echo "🔍 Verifying Day 16: Server CRUD Operations"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the right directory
if [ ! -d "day16-server-crud" ]; then
    print_error "Please run this script from the day16 directory"
    exit 1
fi

cd day16-server-crud

# Function to check if service is running
check_service() {
    local port=$1
    local service_name=$2
    local url=$3
    
    if curl -s "$url" > /dev/null; then
        print_success "$service_name is running on port $port"
        return 0
    else
        print_error "$service_name is not responding on port $port"
        return 1
    fi
}

# Check backend
print_status "Checking backend service..."
if check_service 8000 "Backend" "http://localhost:8000/"; then
    # Test API endpoints
    print_status "Testing API endpoints..."
    
    # Test root endpoint
    if curl -s "http://localhost:8000/" | grep -q "Server Management API"; then
        print_success "API root endpoint working"
    else
        print_error "API root endpoint not working"
    fi
    
    # Test servers endpoint
    if curl -s "http://localhost:8000/api/servers/" | grep -q "servers"; then
        print_success "API servers endpoint working"
    else
        print_error "API servers endpoint not working"
    fi
fi

# Check frontend
print_status "Checking frontend service..."
if check_service 3000 "Frontend" "http://localhost:3000/"; then
    print_success "Frontend is accessible"
fi

# Check Redis
print_status "Checking Redis service..."
if redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is running"
else
    print_error "Redis is not running"
fi

# Check database
print_status "Checking database..."
cd backend
source venv/bin/activate
if python -c "
from app.core.database import engine
from app.models import server, audit
try:
    # Try to query the database
    from sqlalchemy.orm import Session
    session = Session(engine)
    session.execute('SELECT 1')
    session.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"; then
    print_success "Database is accessible"
else
    print_error "Database is not accessible"
fi
cd ..

# Run a quick test
print_status "Running quick integration test..."
if python3 demo_data.py > /dev/null 2>&1; then
    print_success "Integration test passed"
else
    print_error "Integration test failed"
fi

echo ""
print_success "Verification completed!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
