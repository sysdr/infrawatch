#!/bin/bash

echo "========================================="
echo "Starting Automation Integration System"
echo "========================================="

# Always use the directory where this script lives (automation_integration)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Stop any existing backend/frontend so port 8000 is free
echo "Stopping any existing services..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
sleep 2

# Start backend
echo "Starting backend..."
source backend/venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

# Start frontend (must run from frontend dir; npx avoids "Permission denied" on react-scripts)
echo "Starting frontend..."
cd "$PROJECT_DIR/frontend"
npx react-scripts start &
FRONTEND_PID=$!
cd "$PROJECT_DIR"

echo ""
echo "========================================="
echo "  Frontend (Dashboard):  http://localhost:3000"
echo "  Backend API:           http://localhost:8000"
echo "========================================="
echo "API Docs: http://localhost:8000/docs"
echo "To stop:   ./stop.sh"
echo "========================================="

wait
