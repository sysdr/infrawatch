#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Security Testing Platform Build ==="

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "Error: frontend directory not found"
    exit 1
fi

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
cd "$SCRIPT_DIR/backend"
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "Initializing database..."
cd "$SCRIPT_DIR/backend"
export PYTHONPATH="$SCRIPT_DIR/backend:$PYTHONPATH"
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"

echo "Starting backend server..."
cd "$SCRIPT_DIR/backend"
export PYTHONPATH="$SCRIPT_DIR/backend:$PYTHONPATH"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 5

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd "$SCRIPT_DIR/frontend"
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found"
    exit 1
fi
npm install

echo "Starting frontend..."
cd "$SCRIPT_DIR/frontend"
BROWSER=none npm start &
FRONTEND_PID=$!

echo ""
echo "=== Build Complete ==="
echo "Backend running on: http://localhost:8000"
echo "Frontend running on: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

wait
