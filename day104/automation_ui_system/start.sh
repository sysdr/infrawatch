#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting Automation UI System..."

if command -v docker &> /dev/null; then
    if docker compose up -d 2>/dev/null; then
        echo "Services started with Docker."
        echo "Backend: http://localhost:8000  Frontend: http://localhost:3000"
        exit 0
    fi
fi

# Local start (no Docker)
echo "Starting local services..."
cd "$SCRIPT_DIR/backend"
if [ -d venv ]; then
    (cd "$SCRIPT_DIR/backend" && PYTHONPATH=. venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000) &
    (cd "$SCRIPT_DIR/backend" && PYTHONPATH=. venv/bin/celery -A app.workers.celery_app worker --loglevel=info) &
fi
cd "$SCRIPT_DIR/frontend"
if [ -f node_modules/react-scripts/bin/react-scripts.js ]; then
    (PORT=3000 HOST=0.0.0.0 node "$SCRIPT_DIR/frontend/node_modules/react-scripts/bin/react-scripts.js" start) &
else
    [ -d node_modules ] && (npm start &) || true
fi
cd "$SCRIPT_DIR"
echo "Open in browser: http://localhost:3000  (Backend: http://localhost:8000)"
echo "To stop: $SCRIPT_DIR/stop.sh"
