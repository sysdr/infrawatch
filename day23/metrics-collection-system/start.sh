#!/bin/bash

echo "=== Starting Metrics Collection Engine ==="

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies  
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Set Python path
export PYTHONPATH="${PWD}/backend/src:$PYTHONPATH"

# Start backend
echo "Starting backend..."
cd backend
python src/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Start system agent
echo "Starting system agent..."
cd agents/system-agent
python system_agent.py system-agent-1 &
AGENT1_PID=$!
cd ../..

# Start custom agent
echo "Starting custom agent..."
cd agents/custom-agent
python custom_agent.py custom-agent-1 &
AGENT2_PID=$!
cd ../..

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid
echo $AGENT1_PID > agent1.pid
echo $AGENT2_PID > agent2.pid

echo "=== System Started ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
wait
