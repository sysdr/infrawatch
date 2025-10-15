#!/bin/bash

echo "🚀 Starting Alert System Integration..."

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "🔌 WebSocket: ws://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all services"

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for interrupt
wait
