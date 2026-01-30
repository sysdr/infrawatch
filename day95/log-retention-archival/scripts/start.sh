#!/bin/bash
# Start backend and frontend with full path; check for duplicate services first.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Check for duplicate services (ports 8000, 3000)
check_port() {
  local port=$1
  if command -v ss >/dev/null 2>&1; then
    ss -tlnp 2>/dev/null | grep -q ":$port " && return 0
  elif command -v netstat >/dev/null 2>&1; then
    netstat -tlnp 2>/dev/null | grep -q ":$port " && return 0
  fi
  return 1
}

if check_port 8000; then
  echo "WARNING: Port 8000 already in use (backend may already be running)."
  if [ "${KILL_DUPLICATES:-0}" = "1" ]; then
    pkill -f "api/main.py" 2>/dev/null || true
    sleep 2
  else
    echo "Set KILL_DUPLICATES=1 to auto-kill, or run: pkill -f 'api/main.py'"
    echo "Skipping backend start."
    SKIP_BACKEND=1
  fi
fi

if check_port 3000; then
  echo "WARNING: Port 3000 already in use (frontend may already be running)."
  if [ "${KILL_DUPLICATES:-0}" = "1" ]; then
    pkill -f "react-scripts" 2>/dev/null || true
    sleep 2
  else
    echo "Set KILL_DUPLICATES=1 to auto-kill. Skipping frontend start."
    SKIP_FRONTEND=1
  fi
fi

echo "Project root: $PROJECT_ROOT"
BACKEND_PID=""
FRONTEND_PID=""

if [ "${SKIP_BACKEND:-0}" != "1" ]; then
  echo "Starting backend from $BACKEND_DIR ..."
  cd "$BACKEND_DIR"
  if [ -d "venv" ]; then
    source venv/bin/activate
  fi
  export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
  python api/main.py &
  BACKEND_PID=$!
  echo "Backend PID: $BACKEND_PID"
fi

if [ "${SKIP_FRONTEND:-0}" != "1" ]; then
  echo "Starting frontend from $FRONTEND_DIR ..."
  cd "$FRONTEND_DIR"
  if [ ! -d node_modules ] || [ ! -f node_modules/.bin/react-scripts ]; then
    echo "Installing frontend dependencies (npm install)..."
    npm install
  fi
  chmod -R +x node_modules/.bin 2>/dev/null || true
  export HOST=0.0.0.0
  export DANGEROUSLY_DISABLE_HOST_CHECK=true
  npx react-scripts start &
  FRONTEND_PID=$!
  echo "Frontend PID: $FRONTEND_PID"
fi

echo ""
echo "Backend API:  http://localhost:8000"
echo "Dashboard:    http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" EXIT
wait
