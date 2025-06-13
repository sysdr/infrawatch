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
