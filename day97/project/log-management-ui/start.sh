#!/bin/bash
# Start Log Management UI - backend and frontend
# Requires: PostgreSQL, Redis running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for existing processes
if pgrep -f "uvicorn.*8000" > /dev/null; then
    echo "Backend already running on port 8000. Stopping..."
    pkill -f "uvicorn.*8000" 2>/dev/null || true
    sleep 2
fi

# Start backend
echo "Starting backend..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
cd "$SCRIPT_DIR"
PYTHONPATH=. nohup uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

# Wait for backend
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend ready!"
        break
    fi
    sleep 1
done

# Start frontend (HOST=0.0.0.0 for WSL2 - accessible from Windows browser)
echo "Starting frontend..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
HOST=0.0.0.0 npm start &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "========================================"
echo "Application Started!"
echo "========================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000 (also try http://$(hostname -I | awk '{print $1}'):3000 from Windows)"
echo "API Docs: http://localhost:8000/docs"
echo ""
