#!/bin/bash
# Start Day 112 Analytics backend and frontend (full path, no duplicates)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="day112-analytics"
BACKEND_PORT=8112
FRONTEND_PORT=3112
VENV="$SCRIPT_DIR/$PROJECT/venv"
PID_FILE="$SCRIPT_DIR/$PROJECT/.pids"
BACKEND_ABS="$SCRIPT_DIR/$PROJECT/backend"
FRONTEND_ABS="$SCRIPT_DIR/$PROJECT/frontend"

if [ ! -d "$BACKEND_ABS" ] || [ ! -d "$FRONTEND_ABS" ]; then
  echo "Error: Run setup.sh first to create $PROJECT."
  exit 1
fi

# Kill existing processes on our ports
for port in $BACKEND_PORT $FRONTEND_PORT; do
  existing=$(lsof -ti ":$port" 2>/dev/null || true)
  if [ -n "$existing" ]; then
    echo "Killing existing process on port $port"
    kill $existing 2>/dev/null || true
    sleep 2
  fi
done

source "$VENV/bin/activate"

mkdir -p "$BACKEND_ABS/models"
cd "$BACKEND_ABS"
nohup env PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$SCRIPT_DIR/$PROJECT/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

sleep 3
curl -s "http://localhost:$BACKEND_PORT/health" >/dev/null || true

cd "$FRONTEND_ABS"
nohup npm run dev > "$SCRIPT_DIR/$PROJECT/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"
disown -a 2>/dev/null || true

echo "$BACKEND_PID $FRONTEND_PID" > "$PID_FILE"
echo "Backend: http://localhost:$BACKEND_PORT"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "PIDs saved to $PID_FILE. Run ./stop.sh to stop."
