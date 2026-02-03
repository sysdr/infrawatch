#!/bin/bash
# Serve the working dashboard (no npm build required)
# Uses: Python backend + static HTML dashboard

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop existing
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null
sleep 2

# Start backend
echo "Starting backend..."
cd backend && source venv/bin/activate && cd ..
PYTHONPATH=. nohup uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# Wait for backend
for i in {1..15}; do
  curl -s http://localhost:8000/health > /dev/null 2>&1 && break
  sleep 1
done

# Serve dashboard
echo "Serving dashboard..."
cd frontend/public
python3 -m http.server 3000 --bind 0.0.0.0 &
cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo "Dashboard Ready!"
echo "========================================"
echo "Open in browser: http://localhost:3000/dashboard.html"
echo "Backend API:     http://localhost:8000"
echo ""
