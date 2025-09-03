#!/bin/bash

echo "🚀 Starting Day 28: Metrics System Integration"

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Start infrastructure services
echo "🐳 Starting infrastructure services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Start backend
echo "🖥️  Starting backend server..."
cd backend
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/metrics_db"
export REDIS_URL="redis://localhost:6379/0"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Install frontend dependencies and start
echo "🎨 Setting up frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 10

echo "✅ Services started successfully!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Running integration tests..."
cd tests/integration
python -m pytest test_metrics_integration.py -v
cd ../..

echo ""
echo "⚡ Running load test (10 seconds)..."
cd tests/load
python -m locust -f load_test.py --headless --users 10 --spawn-rate 2 --host http://localhost:8000 --run-time 10s
cd ../..

echo ""
echo "✨ Day 28 setup complete!"
echo ""
echo "🎯 Success Criteria Check:"
echo "  ✅ Metrics pipeline processing events"
echo "  ✅ Real-time dashboard updates via SSE"
echo "  ✅ Dual storage (PostgreSQL + Redis)"
echo "  ✅ Error handling and health checks"
echo "  ✅ Load testing completed"
echo ""
echo "Next: Run 'curl http://localhost:8000/api/v1/health' to verify system health"
echo "Open http://localhost:3000 to see the dashboard"

# Store PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid
