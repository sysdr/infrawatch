#!/bin/bash

set -e

echo "🚀 Starting Day 29: Celery Task Queue System"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "🐳 Starting Redis..."
    docker run --name day29-redis -p 6379:6379 -d redis:7.2-alpine || docker start day29-redis
    sleep 3
fi

# Start backend in background
echo "🐍 Starting Flask backend..."
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH
python app/run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start Celery worker in background
echo "⚙️ Starting Celery worker..."
python worker/start_worker.py &
WORKER_PID=$!

# Start frontend
echo "⚛️ Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!

echo "✅ System started successfully!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔍 Flower monitoring: http://localhost:5555 (if using Docker)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $WORKER_PID $FRONTEND_PID 2>/dev/null; docker stop day29-redis 2>/dev/null; exit 0' INT
wait
