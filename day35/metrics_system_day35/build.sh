#!/bin/bash

set -e

echo "🏗️  Building Day 35: Background Processing Integration"
echo "=================================================="

# Check if Python 3.11+ is available
if ! command -v python3.11 &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3.11+ required but not found"
        exit 1
    fi
    PYTHON_CMD=python3
else
    PYTHON_CMD=python3.11
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js required but not found"
    exit 1
fi

echo "📦 Setting up Python virtual environment..."
cd backend
$PYTHON_CMD -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🧪 Running Python tests..."
python -m pytest tests/ -v

echo "🚀 Starting backend services..."

# Kill any existing processes on required ports
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn.*8000" || true
pkill -f "celery.*worker" || true
pkill -f "npm.*start" || true
sleep 2
# Start PostgreSQL and Redis (assuming they're already running)
# In production, these would be managed by Docker Compose

echo "🗄️  Setting up database..."
python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Start backend server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Start Celery worker in background
celery -A app.workers.celery_app worker --loglevel=info --concurrency=4 &
WORKER_PID=$!
echo "Celery worker started with PID: $WORKER_PID"

echo "📝 Backend PIDs saved to ../pids.txt"
echo "$BACKEND_PID" > ../pids.txt
echo "$WORKER_PID" >> ../pids.txt

cd ../frontend

echo "📦 Installing Node.js dependencies..."
npm install

echo "🧪 Running frontend tests..."
npm test -- --watchAll=false --passWithNoTests

echo "🚀 Starting frontend server..."
npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
echo "$FRONTEND_PID" >> ../pids.txt

cd ..

echo ""
echo "✅ BUILD SUCCESSFUL!"
echo "=================================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "📊 Health Check: http://localhost:8000/api/health"
echo ""
echo "📋 Test the system:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Create Task' to add a new background task"
echo "3. Watch real-time updates in the dashboard"
echo "4. Check task processing in the Tasks tab"
echo ""
echo "🛑 To stop all services, run: ./stop.sh"
echo ""

# Wait a bit for services to start
sleep 3

echo "🔍 Verifying services are running..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API not responding"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend not responding"
fi

echo ""
echo "📚 DEMO INSTRUCTIONS:"
echo "1. Visit http://localhost:3000"
echo "2. Observe the dashboard with real-time metrics"
echo "3. Create different types of tasks:"
echo "   - System metrics collection"
echo "   - CSV processing (use sample JSON payload)"
echo "   - Report generation"
echo "4. Watch tasks move through the pipeline"
echo "5. Check WebSocket updates for real-time monitoring"
echo ""
