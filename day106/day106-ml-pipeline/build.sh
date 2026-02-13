#!/bin/bash
# Day 106 ML Pipeline - Build script (uses full paths)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Building Day 106 ML Pipeline"
echo "========================================="

# Stop any existing services
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite --port 3106" 2>/dev/null || true
sleep 1

# Backend setup
echo "Setting up backend..."
cd "$SCRIPT_DIR"
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r backend/requirements.txt

# Run backend tests
echo "Running backend tests..."
cd "$SCRIPT_DIR/backend"
PYTHONPATH=. "$SCRIPT_DIR/venv/bin/python" -m pytest tests/ -v --tb=short 2>&1 | tail -20
TEST_EXIT=${PIPESTATUS[0]}
cd "$SCRIPT_DIR"

# Start backend
echo "Starting backend..."
cd "$SCRIPT_DIR/backend"
PYTHONPATH=. "$SCRIPT_DIR/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8106 --log-level warning &
sleep 5

# Train pipeline
echo "Training ML pipeline..."
curl -s -X POST "http://localhost:8106/api/v1/ml/train?n_samples=500" > /dev/null
echo "Pipeline trained"

# Frontend setup
echo "Setting up frontend..."
cd "$SCRIPT_DIR/frontend"
npm install --silent
echo "Starting frontend..."
npm run dev &
sleep 5

cd "$SCRIPT_DIR"
echo ""
echo "========================================="
echo "Day 106 ML Pipeline - Running!"
echo "Backend:   http://localhost:8106"
echo "Dashboard: http://localhost:3106"
echo "API Docs:  http://localhost:8106/docs"
echo "Stop:      $SCRIPT_DIR/stop.sh"
echo "========================================="
