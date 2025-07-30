#!/bin/bash

# Day 16: Server CRUD Operations - Start Script
# This script sets up the environment, installs dependencies, builds, tests, and launches the application

set -e

echo "🚀 Starting Day 16: Server CRUD Operations"
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

# Store PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""
REDIS_PID=""

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up processes..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$REDIS_PID" ]; then
        kill $REDIS_PID 2>/dev/null || true
    fi
    print_success "Cleanup completed"
}

# Set trap for cleanup
trap cleanup EXIT

# Step 1: Backend Setup
print_status "Step 1: Setting up Python backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Set up SQLite database
print_status "Setting up SQLite database..."
export DATABASE_URL="sqlite:///./server_management.db"
python -c "
from app.core.database import engine
from app.models import server, audit
server.Base.metadata.create_all(bind=engine)
audit.Base.metadata.create_all(bind=engine)
print('SQLite database tables created successfully!')
"
print_success "Database setup completed"

cd ..

# Step 2: Frontend Setup
print_status "Step 2: Setting up React frontend..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
else
    print_status "Node.js dependencies already installed"
fi

cd ..

# Step 3: Start Redis (optional)
print_status "Step 3: Starting Redis (optional)..."
if command -v redis-server >/dev/null 2>&1; then
    if ! pgrep -x "redis-server" > /dev/null; then
        print_status "Starting Redis server..."
        redis-server --daemonize yes
        REDIS_PID=$(pgrep redis-server)
        print_success "Redis started (PID: $REDIS_PID)"
    else
        print_status "Redis is already running"
    fi
else
    print_warning "Redis not found - skipping Redis startup (optional for this demo)"
fi

# Step 4: Run Tests
print_status "Step 4: Running tests..."
echo "Running backend tests..."
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
PYTHONPATH=$PYTHONPATH:. python -m pytest tests/ -v --tb=short
cd ..

echo "Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false --passWithNoTests
cd ..

print_success "All tests passed!"

# Step 5: Start Backend Server
print_status "Step 5: Starting backend server..."
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./server_management.db"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/ > /dev/null; then
        print_success "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Step 6: Start Frontend Server
print_status "Step 6: Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
print_status "Waiting for frontend to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null; then
        print_success "Frontend is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        print_warning "Frontend may still be starting up..."
    fi
    sleep 1
done

# Step 7: Load Demo Data
print_status "Step 7: Loading demo data..."
sleep 5  # Give services time to fully start
export DATABASE_URL="sqlite:///./backend/server_management.db"
python3 demo_data.py

# Step 8: Display Information
echo ""
echo "🎉 Application is now running!"
echo "=========================================="
echo "📊 Dashboard:     http://localhost:3000"
echo "🔧 API:          http://localhost:8000"
echo "📖 API Docs:     http://localhost:8000/docs"
echo "🧪 Test Coverage: http://localhost:3000/coverage"
echo ""
echo "📋 Services Status:"
echo "   Backend (PID: $BACKEND_PID): $(ps -p $BACKEND_PID >/dev/null && echo "✅ Running" || echo "❌ Stopped")"
echo "   Frontend (PID: $FRONTEND_PID): $(ps -p $FRONTEND_PID >/dev/null && echo "✅ Running" || echo "❌ Stopped")"
if command -v redis-server >/dev/null 2>&1; then
    echo "   Redis: $(pgrep redis-server >/dev/null && echo "✅ Running" || echo "❌ Stopped")"
else
    echo "   Redis: ⚠️  Not installed (optional)"
fi
echo ""
echo "🗄️  Database: SQLite (server_management.db)"
echo ""
echo "🛑 To stop all services, run: ./stop.sh"
echo "🔄 To restart, run: ./stop.sh && ./start.sh"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running and handle cleanup
wait
