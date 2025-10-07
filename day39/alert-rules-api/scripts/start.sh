#!/bin/bash

set -e

echo "🚀 Starting Alert Rules API Application..."

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend
echo "🌐 Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Application started successfully!"
echo "📋 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"

# Wait for user interrupt
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait
