#!/bin/bash

echo "🚀 Building Notification UI System..."

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
cd frontend
npm install
cd ..

echo "✅ Dependencies installed"

# Create start script
cat > start.sh << 'EOFSTART'
#!/bin/bash

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Notification UI System..."

# Check if services are already running
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo "⚠️  Backend is already running!"
    exit 1
fi

if pgrep -f "vite" > /dev/null; then
    echo "⚠️  Frontend is already running!"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./build.sh first"
    exit 1
fi

# Check if backend dependencies are installed
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Backend requirements.txt not found"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not installed. Please run ./build.sh first"
    exit 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Start backend in background
cd "$SCRIPT_DIR/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start. Check backend.log for details"
    exit 1
fi

# Check if backend is responding
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend may not be fully ready yet"
else
    echo "✅ Backend is healthy"
fi

# Start frontend in background
cd "$SCRIPT_DIR/frontend"
npm run dev > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Wait a bit for frontend to start
sleep 3

# Check if frontend started successfully
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "❌ Frontend failed to start. Check frontend.log for details"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ System started!"
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Logs:"
echo "  Backend:  $SCRIPT_DIR/backend.log"
echo "  Frontend: $SCRIPT_DIR/frontend.log"

# Save PIDs for stop script
echo $BACKEND_PID > "$SCRIPT_DIR/backend.pid"
echo $FRONTEND_PID > "$SCRIPT_DIR/frontend.pid"

# Keep script running
wait
EOFSTART

chmod +x start.sh

# Create stop script
cat > stop.sh << 'EOFSTOP'
#!/bin/bash

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping Notification UI System..."

# Kill backend
if [ -f "$SCRIPT_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped (PID: $BACKEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/backend.pid"
fi

# Kill frontend
if [ -f "$SCRIPT_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/frontend.pid"
fi

# Kill any remaining processes by name
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    pkill -f "uvicorn.*app.main:app"
    echo "✅ Cleaned up remaining uvicorn processes"
fi

if pgrep -f "vite" > /dev/null; then
    pkill -f "vite"
    echo "✅ Cleaned up remaining vite processes"
fi

echo "✅ System stopped"
EOFSTOP

chmod +x stop.sh

echo "✅ Build completed!"
echo ""
echo "📋 Commands:"
echo "  ./start.sh  - Start the system"
echo "  ./stop.sh   - Stop the system"
echo ""
echo "🔗 URLs (after starting):"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"

