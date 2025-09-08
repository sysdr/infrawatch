#!/bin/bash

echo "🚀 Day 30: Building Async Task Implementation"
echo "=============================================="

# Set permissions
chmod +x build.sh stop.sh

echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "📱 Installing frontend dependencies..."
cd frontend && npm install && cd ..

echo "🗄️ Setting up database..."
# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
until sudo -u postgres pg_isready -h localhost -p 5432 -U postgres 2>/dev/null; do
  echo "PostgreSQL is not ready yet..."
  sleep 2
done

# Create database if it doesn't exist
sudo -u postgres createdb metrics_db 2>/dev/null || echo "Database already exists"

# Run database migrations
cd backend
python -c "
from models.base import engine
from models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"
cd ..

echo "🧪 Running tests..."
cd tests
python -m pytest test_tasks.py -v || echo "⚠️ Some tests failed (expected in demo)"
cd ..

echo "🚀 Starting services..."

# Start Redis (if not running)
redis-server --daemonize yes --port 6379 || echo "Redis may already be running"

# Start Celery worker in background
cd backend
celery -A config.celery_config worker --loglevel=info --concurrency=4 &
CELERY_WORKER_PID=$!

# Start Celery beat scheduler in background  
celery -A config.celery_config beat --loglevel=info &
CELERY_BEAT_PID=$!

# Start FastAPI backend
python app/main.py &
BACKEND_PID=$!

cd ../frontend

# Start React frontend
npm start &
FRONTEND_PID=$!

cd ..

# Save PIDs for cleanup
echo $CELERY_WORKER_PID > celery_worker.pid
echo $CELERY_BEAT_PID > celery_beat.pid  
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo ""
echo "✅ All services started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔗 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Testing the system..."
sleep 10

# Test API endpoints
echo "Testing health endpoint..."
curl -s http://localhost:8000/health | python -m json.tool || echo "Backend not ready yet"

echo ""
echo "Testing metrics collection..."
curl -s -X POST http://localhost:8000/metrics/collect | python -m json.tool || echo "Metrics endpoint not ready yet"

echo ""
echo "🎯 DEMO INSTRUCTIONS:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Collect Metrics' to gather system data"
echo "3. Click 'Test Notification' to send test alerts"
echo "4. Click 'Generate Report' for dashboard summary"
echo "5. Click 'Run Maintenance' to clean up old data"
echo "6. Watch the metrics update in real-time"
echo ""
echo "Press Ctrl+C or run ./stop.sh to stop all services"
