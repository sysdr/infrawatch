#!/bin/bash
# Start Day 113 Backend Performance services (full path, no duplicates)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_ABS="$PROJECT_DIR/backend"
FRONTEND_ABS="$PROJECT_DIR/frontend"
VENV="$BACKEND_ABS/.venv"
BACKEND_PORT=8000
FRONTEND_PORT=3000

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'
info()  { echo -e "${CYAN}[start]${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }

if [ ! -d "$BACKEND_ABS" ]; then
  echo "Error: Run ../setup.sh from day113 root first."
  exit 1
fi

# Avoid duplicate backend
if [ -f /tmp/day113_backend.pid ]; then
  PID=$(cat /tmp/day113_backend.pid)
  if kill -0 "$PID" 2>/dev/null; then
    info "Backend already running (pid $PID). Use ../setup.sh --stop from day113 root to stop."
  else
    rm -f /tmp/day113_backend.pid
  fi
fi

# Avoid duplicate frontend
if [ -f /tmp/day113_frontend.pid ]; then
  PID=$(cat /tmp/day113_frontend.pid)
  if kill -0 "$PID" 2>/dev/null; then
    info "Frontend already running (pid $PID). Use ../setup.sh --stop from day113 root to stop."
  else
    rm -f /tmp/day113_frontend.pid
  fi
fi

# Start infra (Docker) if present
if [ -f "$PROJECT_DIR/docker/docker-compose.yml" ] && command -v docker &>/dev/null; then
  info "Ensuring PostgreSQL and Redis are up..."
  cd "$PROJECT_DIR/docker"
  docker compose up -d postgres redis 2>/dev/null || true
  cd "$SCRIPT_DIR"
fi

# Start backend if not running
if [ ! -f /tmp/day113_backend.pid ] || ! kill -0 "$(cat /tmp/day113_backend.pid)" 2>/dev/null; then
  info "Starting FastAPI backend..."
  cd "$BACKEND_ABS"
  nohup "$VENV/bin/uvicorn" app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > /tmp/day113_backend.log 2>&1 &
  echo $! > /tmp/day113_backend.pid
  cd "$SCRIPT_DIR"
  sleep 3
  if curl -sf "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
    ok "Backend: http://localhost:$BACKEND_PORT"
  else
    echo -e "${YELLOW}[start]${NC} Backend starting — tail /tmp/day113_backend.log"
  fi
else
  ok "Backend already running: http://localhost:$BACKEND_PORT"
fi

# Start frontend if node available and not running
if command -v node &>/dev/null && [ -d "$FRONTEND_ABS" ]; then
  if [ ! -f /tmp/day113_frontend.pid ] || ! kill -0 "$(cat /tmp/day113_frontend.pid)" 2>/dev/null; then
    info "Starting React frontend..."
    cd "$FRONTEND_ABS"
    BROWSER=none nohup npm start > /tmp/day113_frontend.log 2>&1 &
    echo $! > /tmp/day113_frontend.pid
    cd "$SCRIPT_DIR"
    sleep 5
    if curl -sf "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
      ok "Frontend: http://localhost:$FRONTEND_PORT"
    else
      echo -e "${YELLOW}[start]${NC} Frontend starting — tail /tmp/day113_frontend.log"
    fi
  else
    ok "Frontend already running: http://localhost:$FRONTEND_PORT"
  fi
else
  info "Node.js not found or no frontend — skipping."
fi

echo ""
ok "Services started. To stop: ../setup.sh --stop (from day113 root)"
