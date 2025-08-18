#!/bin/bash

echo "🚀 Starting Metrics Data Models System"

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

# Start PostgreSQL and Redis (using Docker)
docker-compose up -d postgres redis

# Wait for databases to be ready
echo "⏳ Waiting for databases..."
sleep 10

# Start backend server
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Start frontend server
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo ""
echo "PIDs saved for cleanup:"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

# Save PIDs for stop script
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

wait
