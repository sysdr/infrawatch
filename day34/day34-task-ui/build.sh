#!/bin/bash
set -e

echo "🏗️  Building Task Management UI Dashboard"
echo "========================================"

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Dependencies check passed"

# Setup Python environment
echo "🐍 Setting up Python environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Starting Redis (if needed)..."
if ! pgrep -x "redis-server" > /dev/null; then
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes
        echo "✅ Redis started"
    else
        echo "⚠️  Redis not found. Install Redis or use Docker version."
    fi
fi

echo "🚀 Starting backend..."
python app/main.py &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

cd ../frontend

echo "📦 Installing frontend dependencies..."
npm install

echo "🎨 Starting frontend..."
npm start &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

echo ""
echo "🎉 Build Complete!"
echo "================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "WebSocket: ws://localhost:8000/ws"
echo ""
echo "✅ Ready for testing and demo!"
echo ""
echo "To stop services, run: ./stop.sh"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
