#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "Starting Security Log Management"
echo "=================================="

# Avoid duplicate: stop if already running
if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
  OLD_PID=$(cat "$SCRIPT_DIR/.backend.pid")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Backend already running (PID $OLD_PID). Use ./stop.sh first to restart."
    exit 1
  fi
  rm -f "$SCRIPT_DIR/.backend.pid"
fi
if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
  OLD_PID=$(cat "$SCRIPT_DIR/.frontend.pid")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Frontend already running (PID $OLD_PID). Use ./stop.sh first to restart."
    exit 1
  fi
  rm -f "$SCRIPT_DIR/.frontend.pid"
fi

# Backend (use venv's uvicorn; ensure deps installed)
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
  echo "Run ./build.sh first to create venv and install dependencies."
  exit 1
fi
if ! "$SCRIPT_DIR/backend/venv/bin/python" -c "import fastapi" 2>/dev/null; then
  echo "Installing backend dependencies..."
  "$SCRIPT_DIR/backend/venv/bin/pip" install -q -r requirements.txt
fi
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/security_logs}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
"$SCRIPT_DIR/backend/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
echo "Backend started (PID: $BACKEND_PID)"

# Frontend: prefer React if built, else serve simple dashboard
if [ -d "$SCRIPT_DIR/frontend/build" ]; then
  cd "$SCRIPT_DIR/frontend"
  npx -y serve -s build -l 3000 &
  FRONTEND_PID=$!
  echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
  echo "Frontend started (React build, PID: $FRONTEND_PID)"
elif [ -d "$SCRIPT_DIR/frontend/node_modules" ]; then
  cd "$SCRIPT_DIR/frontend"
  PORT=3000 HOST=0.0.0.0 npm start &
  FRONTEND_PID=$!
  echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
  echo "Frontend started (React dev, PID: $FRONTEND_PID)"
else
  # Fallback: serve simple dashboard.html with Python
  cd "$SCRIPT_DIR"
  python3 -m http.server 3000 --bind 0.0.0.0 &
  FRONTEND_PID=$!
  echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
  echo "Dashboard started (simple HTML at /dashboard.html, PID: $FRONTEND_PID)"
fi

cd "$SCRIPT_DIR"
echo ""
echo "Backend:   http://localhost:8000  (docs: http://localhost:8000/docs)"
echo "Dashboard: http://localhost:3000/dashboard.html"
echo "Stop:      ./stop.sh"
echo ""
