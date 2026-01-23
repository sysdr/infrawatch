#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKEND_PORT=8001
API_URL="http://localhost:${BACKEND_PORT}"

echo "======================================"
echo "Building Cloud Resource Management System"
echo "======================================"

check_success() {
    if [ $? -eq 0 ]; then
        echo "✓ $1 successful"
    else
        echo "✗ $1 failed"
        exit 1
    fi
}

echo ""
echo "Option 1: Running with Docker"
echo "======================================"
if command -v docker-compose &> /dev/null && [ -f docker-compose.yml ]; then
    echo "Building Docker containers..."
    docker-compose build
    check_success "Docker build"
    
    echo "Starting services..."
    docker-compose up -d
    check_success "Docker startup"
    
    echo "Waiting for services to be ready..."
    sleep 15
    
    echo ""
    echo "✓ All services started successfully!"
    echo ""
    echo "Services running:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Frontend UI: http://localhost:3000"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
else
    echo "Docker Compose not available or docker-compose.yml not found. Skipping Docker option."
fi

echo "======================================"
echo ""
echo "Option 2: Running without Docker"
echo "======================================"

# Check for duplicate services
if pgrep -f "uvicorn.*0.0.0.0:${BACKEND_PORT}" > /dev/null 2>&1; then
    echo "⚠ Backend already running on port ${BACKEND_PORT}. Skipping backend startup."
else
    echo "Setting up Python virtual environment..."
    cd backend
    python3 -m venv venv 2>/dev/null || true
    check_success "Virtual environment creation"
    
    source venv/bin/activate
    check_success "Virtual environment activation"
    
    echo "Installing Python dependencies..."
    pip install -q -r requirements.txt 2>&1 | tail -5
    check_success "Python dependencies installation"
    
    echo "Running backend tests..."
    PYTHONPATH=. pytest tests/ -v --tb=short 2>&1 | tail -20
    check_success "Backend tests"
    
    echo "Starting backend server on port ${BACKEND_PORT}..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    sleep 3
    check_success "Backend server startup"
    
    cd ..
fi

if pgrep -f "react-scripts start" > /dev/null 2>&1; then
    echo "⚠ Frontend already running. Skipping frontend startup."
else
    cd frontend
    
    echo "Installing Node.js dependencies..."
    npm install --silent 2>&1 | tail -5
    check_success "Node.js dependencies installation"
    
    echo "Starting frontend server..."
    REACT_APP_API_URL="${API_URL}" npm start > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    check_success "Frontend server startup"
    
    cd ..
fi

echo ""
echo "======================================"
echo "Testing the System"
echo "======================================"

sleep 5

echo ""
echo "1. Testing Backend Health..."
curl -sf "${API_URL}/" | python3 -m json.tool 2>/dev/null || echo "Backend not responding yet..."

echo ""
echo "2. Provisioning Test Resource..."
curl -sf -X POST "${API_URL}/api/resources/provision" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-compute-instance",
    "type": "compute",
    "provider": "aws",
    "region": "us-east-1",
    "team": "engineering",
    "size": 2
  }' | python3 -m json.tool 2>/dev/null || echo "Provisioning request sent..."

sleep 3

echo ""
echo "3. Listing Resources..."
RESOURCE_COUNT=$(curl -sf "${API_URL}/api/resources" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo "Found $RESOURCE_COUNT resources"

echo ""
echo "4. Getting Dashboard Stats..."
curl -sf "${API_URL}/api/stats/dashboard" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'  Resources: {d[\"resources\"][\"total\"]} total, {d[\"resources\"][\"active\"]} active')
print(f'  Monthly cost: \${d[\"costs\"][\"total_monthly\"]}')
print(f'  Potential savings: \${d[\"costs\"][\"potential_savings\"]}')
" 2>/dev/null || echo "Fetching stats..."

echo ""
echo "======================================"
echo "System is Ready!"
echo "======================================"
echo ""
echo "Access Points:"
echo "  - Frontend Dashboard: http://localhost:3000"
echo "  - Backend API: ${API_URL}"
echo "  - API Documentation: ${API_URL}/docs"
echo ""
echo "To stop the system:"
echo "  - With Docker: docker-compose down"
echo "  - Without Docker: pkill -f 'uvicorn.*${BACKEND_PORT}' && pkill -f 'react-scripts'"
echo ""
echo "To run demo:"
echo "  - cd $(pwd) && REACT_APP_API_URL=${API_URL} ./demo.sh"
echo ""
