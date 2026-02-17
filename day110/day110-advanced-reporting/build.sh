#!/bin/bash
set -e

# Run from script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "Building Advanced Reporting System"
echo "======================================"

# Check for duplicate services
check_port() {
  if command -v ss &>/dev/null; then
    ss -tlnp 2>/dev/null | grep -q ":$1 " && return 0
  fi
  if command -v lsof &>/dev/null; then
    lsof -i ":$1" 2>/dev/null | grep -q LISTEN && return 0
  fi
  return 1
}
if check_port 8000; then echo "Port 8000 in use. Run ./stop.sh first."; exit 1; fi
if check_port 3000; then echo "Port 3000 in use. Run ./stop.sh first."; exit 1; fi

# Backend
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

# Run tests (PYTHONPATH so 'app' is importable)
echo "Running backend tests..."
export PYTHONPATH="$(pwd):$PYTHONPATH"
pytest tests/ -v
echo "✓ Backend tests passed"

# Start backend (use venv uvicorn so background job uses correct interpreter)
echo "Starting backend server..."
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✓ Backend running (PID: $BACKEND_PID)"

cd ..

# Frontend
echo "Setting up frontend..."
cd frontend
npm install
echo "✓ Frontend dependencies installed"

# Run tests
echo "Running frontend tests..."
CI=true npm test
echo "✓ Frontend tests passed"

# Start frontend
echo "Starting frontend server..."
npm start &
FRONTEND_PID=$!
echo "✓ Frontend running (PID: $FRONTEND_PID)"

cd ..

echo ""
echo "======================================"
echo "✓ Build Complete!"
echo "======================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: ./stop.sh"
echo ""
echo "Demonstration:"
echo "1. Open http://localhost:3000"
echo "2. Create a template in Templates tab"
echo "3. Create a report in Report Builder"
echo "4. Click Generate to create reports"
echo "5. Schedule reports in Schedules tab"
echo "======================================"

# Save PIDs
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid
