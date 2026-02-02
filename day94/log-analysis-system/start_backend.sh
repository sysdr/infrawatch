#!/bin/bash
# Start backend - run from log-analysis-system directory or anywhere
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"
PORT=8000

# Ensure venv exists
if [ ! -d "venv" ]; then
    echo "Creating venv and installing dependencies..."
    python3 -m venv venv
    ./venv/bin/pip install -q -r requirements.txt
fi

export PYTHONPATH="$SCRIPT_DIR/backend:$PYTHONPATH"
UVICORN="$SCRIPT_DIR/backend/venv/bin/uvicorn"

# Free port 8000 if something is already running (one attempt)
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:${PORT} 2>/dev/null)
  if [ -n "$PIDS" ]; then
    echo "Port ${PORT} in use (PIDs: $PIDS). Stopping existing process..."
    kill -9 $PIDS 2>/dev/null || true
    sleep 2
  fi
fi

# Use SQLite when DATABASE_URL not set (no PostgreSQL required)
export DATABASE_URL="${DATABASE_URL:-sqlite:///./loganalysis.db}"

# Initialize DB
cd "$SCRIPT_DIR/backend"
"$SCRIPT_DIR/backend/venv/bin/python" -c "from app.models.database import init_db; init_db()" 2>/dev/null || true

echo "Starting backend at http://localhost:${PORT}"
echo "  Health: http://localhost:${PORT}/api/health"
echo "  (First start may take ~15 seconds while libraries load.)"
exec "$UVICORN" app.main:app --host 0.0.0.0 --port ${PORT}
