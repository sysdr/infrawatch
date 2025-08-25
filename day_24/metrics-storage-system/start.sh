#!/bin/bash

set -e

echo "🚀 Starting Day 24: Metrics Storage & Retrieval System"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Create environment file
cat > .env << 'ENV_EOF'
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=dev-token-12345
INFLUXDB_ORG=metrics-org
INFLUXDB_BUCKET=metrics-bucket
REDIS_URL=redis://localhost:6379
ENV_EOF

# Start backend
echo "🚀 Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "🚀 Starting frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for stopping
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo ""
echo "🎉 System started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo ""
echo "📋 Test the system:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Check the dashboard for metrics"
echo "3. Test the API endpoints at http://localhost:8000/docs"
echo ""
echo "🛑 To stop: run ./stop.sh"
