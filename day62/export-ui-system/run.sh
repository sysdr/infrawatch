#!/bin/bash

echo "=========================================="
echo "Starting Export UI System"
echo "=========================================="

# Start PostgreSQL (assuming local installation)
echo "Starting PostgreSQL..."
# docker run -d --name export-postgres -e POSTGRES_USER=exportuser -e POSTGRES_PASSWORD=exportpass -e POSTGRES_DB=exportdb -p 5432:5432 postgres:16

# Start Redis
echo "Starting Redis..."
# docker run -d --name export-redis -p 6379:6379 redis:7-alpine

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "System is running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
wait
