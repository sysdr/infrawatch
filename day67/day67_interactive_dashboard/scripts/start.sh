#!/bin/bash

set -e

echo "======================================"
echo "Starting Interactive Dashboard System"
echo "======================================"

# Start backend
echo "🚀 Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend
sleep 5

# Start frontend
echo "🚀 Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Application started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

# Save PIDs
echo $BACKEND_PID > /tmp/dashboard_backend.pid
echo $FRONTEND_PID > /tmp/dashboard_frontend.pid

wait
