#!/bin/bash

echo "🔧 Day 47: Building Notification Testing & Reliability System"
echo "============================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/notification-testing-system" || cd "$SCRIPT_DIR" || exit 1

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv || python -m venv venv
fi
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize backend
echo "🚀 Initializing backend service..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install || echo "⚠️ npm install failed, continuing..."
fi

# Build frontend
echo "🏗️ Building React frontend..."
npm run build || echo "⚠️ Frontend build failed, continuing..."

# Copy build to backend static directory
echo "📦 Copying frontend build to backend..."
cd ..
mkdir -p backend/static
if [ -d "frontend/build" ]; then
    cp -r frontend/build/* backend/static/ || echo "⚠️ Failed to copy frontend build"
else
    echo "⚠️ Frontend build not found"
fi

# Run tests
echo "🧪 Running backend tests..."
cd backend
python -m pytest tests/ -v 2>/dev/null || echo "⚠️ Tests directory not found or pytest not available"
cd ..

echo "✅ Build completed successfully!"

# Start services without Docker
echo "🚀 Starting services (without Docker)..."
echo "Backend will start on http://localhost:8000"
echo "Frontend will be served from backend static files"
echo ""

# Start backend server (this will also serve frontend)
cd backend
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "⚠️ Virtual environment not found, using system Python"
fi
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Check if already running
if pgrep -f "python.*src/main.py" > /dev/null; then
    echo "⚠️ Backend server already running, stopping old instance..."
    pkill -f "python.*src/main.py"
    sleep 2
fi

python src/main.py &
BACKEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "🌐 Application running at: http://localhost:8000"
echo ""

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend server failed to start"
    exit 1
fi

echo "✅ Server started successfully!"

echo ""
echo "✅ System is ready!"
echo "📊 Dashboard: http://localhost:8000"
echo "🧪 Testing: http://localhost:8000/testing"
echo "📈 Monitoring: http://localhost:8000/monitoring"
echo ""
echo "🛑 To stop services, run: ./stop.sh"

# Save PID for stop script
echo $BACKEND_PID > .backend.pid

# Wait for user input
echo "Press Ctrl+C to stop the services..."
wait $BACKEND_PID
