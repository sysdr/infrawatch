#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Building Log Analysis System"
echo "=========================================="

BUILD_TYPE=${1:-local}

if [ "$BUILD_TYPE" == "docker" ]; then
    echo "Building with Docker..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
    echo ""
    echo "✅ System is running!"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "To stop: $SCRIPT_DIR/stop.sh docker"
else
    echo "Building locally..."
    BACKEND_DIR="$SCRIPT_DIR/backend"
    FRONTEND_DIR="$SCRIPT_DIR/frontend"

    # Install backend dependencies
    cd "$BACKEND_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    python3 -c "from app.models.database import init_db; init_db()"

    # Start backend (run from backend dir)
    "$BACKEND_DIR/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --reload --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
    cd "$SCRIPT_DIR"

    # Install frontend dependencies
    cd "$FRONTEND_DIR"
    [ -d node_modules ] || npm install
    export PORT=3001
    export HOST=0.0.0.0
    npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
    cd "$SCRIPT_DIR"

    echo ""
    echo "✅ System is running!"
    echo "Dashboard: http://localhost:3001"
    echo "Backend API: http://localhost:8000"
    echo ""
    echo "To stop: $SCRIPT_DIR/stop.sh"
fi
