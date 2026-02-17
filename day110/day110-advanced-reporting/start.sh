#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "Starting Advanced Reporting System"
echo "======================================"
check_port() {
  if command -v ss &>/dev/null; then ss -tlnp 2>/dev/null | grep -q ":$1 " && return 0; fi
  if command -v lsof &>/dev/null; then lsof -i ":$1" 2>/dev/null | grep -q LISTEN && return 0; fi
  return 1
}
if check_port 8000; then echo "Port 8000 in use. Run ./stop.sh first."; exit 1; fi
if check_port 3000; then echo "Port 3000 in use. Run ./stop.sh first."; exit 1; fi

echo "Starting backend..."
cd backend
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✓ Backend running (PID: $BACKEND_PID)"
echo $BACKEND_PID > ../backend.pid
cd ..

if [ -d frontend/node_modules ]; then
  echo "Starting frontend..."; cd frontend; npm start &
  echo $! > ../frontend.pid; cd ..
else
  echo "Skipping frontend (run ./build.sh first to install)"
  echo "  Frontend URL when running: http://localhost:3000"
fi

echo ""
echo "✓ Start complete"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000 (only if started above)"
echo "  Stop:     ./stop.sh"
