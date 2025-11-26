#!/bin/bash

echo "🚀 Starting Real-time Integration System..."

# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ System started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"

wait
