#!/bin/bash
# Day 106 ML Pipeline - Startup script (uses full paths)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PORT=8106
FRONTEND_PORT=3106

# Kill any existing processes on these ports
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite --port 3106" 2>/dev/null || true
sleep 1

# Use venv; install deps if uvicorn missing
cd "$BACKEND_DIR"
if [ -d "$PROJECT_DIR/venv" ]; then
  export PYTHONPATH="$BACKEND_DIR"
  if [ ! -f "$PROJECT_DIR/venv/bin/uvicorn" ]; then
    echo "Installing backend dependencies..."
    "$PROJECT_DIR/venv/bin/pip" install -q -r "$BACKEND_DIR/requirements.txt"
  fi
  UVICORN="$PROJECT_DIR/venv/bin/uvicorn"
else
  UVICORN="uvicorn"
fi

# Start backend
echo "Starting backend at http://localhost:$BACKEND_PORT"
$UVICORN app.main:app --host 0.0.0.0 --port $BACKEND_PORT --log-level warning &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/day106_backend.pid

# Wait for backend
for i in $(seq 1 30); do
  if curl -s "http://localhost:$BACKEND_PORT/api/v1/health" > /dev/null 2>&1; then
    echo "Backend ready"
    break
  fi
  sleep 1
done

# Train pipeline
echo "Training ML pipeline..."
curl -s -X POST "http://localhost:$BACKEND_PORT/api/v1/ml/train?n_samples=500" > /dev/null
echo "Pipeline trained"

# Start frontend
cd "$FRONTEND_DIR"
echo "Starting frontend at http://localhost:$FRONTEND_PORT"
npm run dev &
echo $! > /tmp/day106_frontend.pid

echo ""
echo "Day 106 ML Pipeline running!"
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  Dashboard: http://localhost:$FRONTEND_PORT"
echo "  Stop: ./stop.sh"
