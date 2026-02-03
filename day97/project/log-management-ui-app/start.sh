#!/bin/bash
# Start Log Management UI - backend and frontend
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

pkill -f "uvicorn.*8000" 2>/dev/null
sleep 2

echo "Starting backend..."
cd backend
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
cd "$SCRIPT_DIR"
PYTHONPATH=. nohup uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

echo "Waiting for backend..."
for i in {1..20}; do
  curl -s http://localhost:8000/health > /dev/null 2>&1 && break
  sleep 1
done

echo "Serving frontend..."
cd frontend/public
HOST=0.0.0.0 python3 -m http.server 3000 --bind 0.0.0.0 &
cd "$SCRIPT_DIR"

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000/dashboard.html"
echo ""
