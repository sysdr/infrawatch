#!/bin/bash
# Start BI Dashboard - run from bi-dashboard directory with full paths
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

# Kill any existing processes on ports
for port in 8000 3000; do
  pid=$(lsof -ti:$port 2>/dev/null) || true
  if [ -n "$pid" ]; then
    echo "Stopping existing process on port $port (PID $pid)"
    kill $pid 2>/dev/null || true
    sleep 2
  fi
done

# Backend: ensure venv and deps
if [ ! -d "$BACKEND/venv" ]; then
  echo "Creating backend venv..."
  python3 -m venv "$BACKEND/venv"
fi
source "$BACKEND/venv/bin/activate"
if ! pip install -q -r "$BACKEND/requirements.txt" 2>/dev/null; then
  echo "Note: venv pip install had issues, trying with system python for server..."
fi

# Init DB and seed (SQLite)
cd "$BACKEND"
export PYTHONPATH="$BACKEND"
python3 -c "
from services.database import init_db, SessionLocal
from services.seeder import DataSeeder
init_db()
db = SessionLocal()
seeder = DataSeeder(db)
seeder.seed_metrics()
seeder.seed_values(90)
db.close()
print('Database seeded.')
"

# Start backend (full path uvicorn; use venv python or fallback to system)
echo "Starting backend at http://localhost:8000"
PYTHON_EXEC="$BACKEND/venv/bin/python3"
if [ ! -x "$PYTHON_EXEC" ] || ! "$PYTHON_EXEC" -c "import fastapi" 2>/dev/null; then
  PYTHON_EXEC="python3"
fi
cd "$BACKEND" && PYTHONPATH="$BACKEND" nohup "$PYTHON_EXEC" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$ROOT/backend.log" 2>&1 &
echo $! > "$ROOT/backend.pid"
sleep 3

# Frontend
if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "Installing frontend deps..."
  (cd "$FRONTEND" && npm install --silent)
fi
echo "Starting frontend at http://localhost:3000"
(cd "$FRONTEND" && nohup npm run dev > "$ROOT/frontend.log" 2>&1 &)
echo $! > "$ROOT/frontend.pid"
sleep 3
echo "Backend: http://localhost:8000  Frontend: http://localhost:3000"
echo "To stop: ./stop.sh"
