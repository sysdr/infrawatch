#!/bin/bash

echo "========================================="
echo "Building Automation Integration System"
echo "========================================="

cd "$(dirname "$0")"

# Setup PostgreSQL
echo "Setting up PostgreSQL..."
if command -v psql &> /dev/null; then
    sudo -u postgres psql -c "CREATE DATABASE automation_db;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER automation WITH PASSWORD 'automation123';" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE automation_db TO automation;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE automation_test_db;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE automation_test_db TO automation;" 2>/dev/null || true
fi

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run backend tests (continue even if tests fail so we can start services)
echo "Running backend tests..."
cd ..
source backend/venv/bin/activate
PYTHONPATH=backend pytest tests/ -v || true

# Start backend
echo "Starting backend..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 5

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install

# Start frontend
echo "Starting frontend..."
npm start &
FRONTEND_PID=$!
cd ..

echo "========================================="
echo "System Started Successfully!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "========================================="
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait
wait
