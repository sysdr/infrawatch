#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Building Alert Processing Pipeline..."
echo "📁 Working directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd "$SCRIPT_DIR/backend"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
cd "$SCRIPT_DIR"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd "$SCRIPT_DIR/frontend"
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
cd "$SCRIPT_DIR"

echo "✅ Build completed successfully!"

# Start services
echo "🚀 Starting Alert Processing Pipeline..."

# Start backend in background
echo "🔧 Starting backend server..."
cd "$SCRIPT_DIR/backend"
source "$SCRIPT_DIR/venv/bin/activate"
python -m app.main &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend in background  
echo "🎨 Starting frontend server..."
cd "$SCRIPT_DIR/frontend"
npm start &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Services started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

# Save PIDs for stop script
echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"

echo "🧪 Running tests..."
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR"
python -m pytest tests/ -v

echo "🎯 Creating test alerts..."
sleep 2

# Create test alerts via API
curl -X POST "http://localhost:8000/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "High CPU Usage",
    "description": "CPU usage exceeded threshold",
    "metric_name": "cpu_usage",
    "service_name": "web-server",
    "current_value": 85.0,
    "threshold_value": 80.0
  }'

curl -X POST "http://localhost:8000/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Connection Pool Full",
    "description": "All database connections are in use",
    "metric_name": "db_connections",
    "service_name": "database",
    "current_value": 100.0,
    "threshold_value": 95.0
  }'

curl -X POST "http://localhost:8000/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Memory Usage High",
    "description": "Memory usage is approaching limit",
    "metric_name": "memory_usage",
    "service_name": "api-gateway",
    "current_value": 92.0,
    "threshold_value": 90.0
  }'

echo "✅ Test alerts created!"
echo "🎉 Demo ready! Visit http://localhost:3000"
echo "📝 Run ./stop.sh to stop all services"

wait
