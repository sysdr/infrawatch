#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Kill existing services on ports 8000 and 3000
for port in 8000 3000; do
    PID=$(lsof -ti:$port 2>/dev/null)
    [ -n "$PID" ] && kill $PID 2>/dev/null && echo "Stopped existing process on port $port"
done
sleep 2

# Start backend
echo "Starting backend..."
cd "$SCRIPT_DIR/backend" || exit 1
[ ! -d "venv" ] && python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null
export DATABASE_URL="${DATABASE_URL:-sqlite:///./metrics.db}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR" || exit 1

sleep 3

# Start frontend (HOST=0.0.0.0 needed for WSL - allows Windows browser to connect)
echo "Starting frontend..."
cd "$SCRIPT_DIR/frontend" || exit 1
[ ! -d "node_modules" ] && npm install
HOST=0.0.0.0 BROWSER=none REACT_APP_API_URL=http://localhost:8000 npm start &
FRONTEND_PID=$!
cd "$SCRIPT_DIR" || exit 1

echo ""
echo "==================================="
echo "Services started:"
echo "  Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "  Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "==================================="
echo "Run ./run_demo.sh to populate dashboard"
