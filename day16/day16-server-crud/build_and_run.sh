#!/bin/bash

echo "🚀 Building and running the application..."

# Install backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start services
echo "Starting PostgreSQL and Redis..."
cd ../docker
docker-compose up -d postgres redis

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run database migrations (create tables)
cd ../backend
source venv/bin/activate
python -c "from app.core.database import engine; from app.models import server, audit; server.Base.metadata.create_all(bind=engine); audit.Base.metadata.create_all(bind=engine); print('Database tables created!')"

# Start backend
echo "Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "🎉 Application is running!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"

# Keep script running
wait $BACKEND_PID $FRONTEND_PID
