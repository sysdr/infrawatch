#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# Check for duplicate services
if pgrep -f "uvicorn app.main:app" >/dev/null 2>&1; then
  echo "[!] Backend (uvicorn) already running. Run ./stop.sh first or use existing."
  exit 1
fi
if pgrep -f "react-scripts start" >/dev/null 2>&1; then
  echo "[!] Frontend (react-scripts) already running. Run ./stop.sh first or use existing."
  exit 1
fi

echo "Starting Day 115 services from $PROJECT_DIR"

# Ensure PostgreSQL is up (for API health and dashboard)
if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
  (cd "$PROJECT_DIR" && docker compose up -d pg-primary 2>/dev/null) || true
  sleep 2
fi

# Backend (full path)
if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
  cd "$BACKEND_DIR"
  . venv/bin/activate
  nohup uvicorn app.main:app --reload --port "$BACKEND_PORT" > /tmp/day115-api.log 2>&1 &
  echo $! > /tmp/day115-api.pid
  echo "[✓] Backend started (port $BACKEND_PORT), PID $(cat /tmp/day115-api.pid)"
else
  echo "[!] Backend venv not found. Run setup.sh first."
  exit 1
fi

# Frontend (full path)
if [ -f "$FRONTEND_DIR/package.json" ]; then
  cd "$FRONTEND_DIR"
  REACT_APP_API_URL="http://localhost:$BACKEND_PORT" nohup npm start > /tmp/day115-frontend.log 2>&1 &
  echo $! > /tmp/day115-frontend.pid
  echo "[✓] Frontend starting (port $FRONTEND_PORT), PID $(cat /tmp/day115-frontend.pid)"
else
  echo "[!] Frontend not found at $FRONTEND_DIR"
  exit 1
fi

echo "Dashboard: http://localhost:$FRONTEND_PORT  API: http://localhost:$BACKEND_PORT"
echo "Logs: tail -f /tmp/day115-api.log  |  tail -f /tmp/day115-frontend.log"
echo "Stop: $PROJECT_DIR/stop.sh"
