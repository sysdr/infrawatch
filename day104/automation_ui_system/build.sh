#!/bin/bash
# Resolve project directory (full path) so scripts work from anywhere
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "Building Automation UI System"
echo "=================================="
echo "Project directory: $SCRIPT_DIR"

# Try Docker first; on credential/metadata errors, suggest fix and fall back to local
if command -v docker &> /dev/null; then
    echo "Docker detected. Building with Docker..."
    if docker compose build 2>&1 && docker compose up -d 2>&1; then
        echo ""
        echo "Waiting for services to be healthy..."
        sleep 15
        echo ""
        echo "System is running!"
        echo "Backend API: http://localhost:8000"
        echo "Frontend UI: http://localhost:3000"
        echo "API Documentation: http://localhost:8000/docs"
        echo "To view logs: docker compose logs -f"
        echo "To stop: $SCRIPT_DIR/stop.sh"
        exit 0
    fi
    echo ""
    echo "Docker build/start failed (often due to credential/network)."
    echo "To fix Docker and retry:  $SCRIPT_DIR/scripts/fix-docker-credentials.sh"
    echo "Falling back to local build..."
fi

# Local build (no set -e so one failure does not stop everything)
echo "Building locally..."
cd "$SCRIPT_DIR/backend"
python3 -m venv venv 2>/dev/null || true
if [ -f venv/bin/activate ]; then
    echo "Installing backend dependencies..."
    "$SCRIPT_DIR/backend/venv/bin/pip" install -r requirements.txt
    PYTHONPATH=. "$SCRIPT_DIR/backend/venv/bin/python" -c "from app.core.database import init_db; init_db()" 2>/dev/null || true
    echo "Starting backend (needs PostgreSQL and Redis)..."
    (cd "$SCRIPT_DIR/backend" && PYTHONPATH=. venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000) &
    (cd "$SCRIPT_DIR/backend" && PYTHONPATH=. venv/bin/celery -A app.workers.celery_app worker --loglevel=info) &
fi
cd "$SCRIPT_DIR/frontend"
echo "Installing frontend dependencies..."
npm install
echo "Starting frontend..."
# nohup + disown so the dev server keeps running after this script exits
# .env sets HOST=0.0.0.0 so it's reachable from Windows when using WSL2
FRONTEND_LOG="$SCRIPT_DIR/frontend/frontend.log"
nohup node "$SCRIPT_DIR/frontend/node_modules/react-scripts/bin/react-scripts.js" start >> "$FRONTEND_LOG" 2>&1 &
disown 2>/dev/null || true
# Wait for dev server to bind so user doesn't hit connection refused
for i in 1 2 3 4 5 6 7 8 9 10 15 20; do
  sleep 1
  if curl -s -o /dev/null --connect-timeout 1 http://127.0.0.1:3000 2>/dev/null; then
    echo "Frontend is up at http://localhost:3000"
    break
  fi
  [ "$i" -eq 20 ] && echo "If connection refused, wait 30s then try http://localhost:3000 again, or see $FRONTEND_LOG"
done
cd "$SCRIPT_DIR"
echo ""
echo "=============================================="
echo "  Open in your browser:  http://localhost:3000"
echo "  (Backend API:          http://localhost:8000)"
echo "  Use the port :3000 — plain 'localhost' will not work."
echo "  To stop: $SCRIPT_DIR/stop.sh"
echo "=============================================="
