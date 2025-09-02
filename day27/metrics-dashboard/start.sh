#!/bin/bash

echo "🚀 Starting Metrics Dashboard"
echo "============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Initialize database
echo "🗄️ Initializing database..."
cd backend
python -c "
from app.models.metrics import Base, engine, SessionLocal, MetricData
import json
from datetime import datetime, timedelta
import random

# Create tables
Base.metadata.create_all(bind=engine)

# Add sample data
db = SessionLocal()
now = datetime.utcnow()

metrics = ['cpu_usage', 'memory_usage', 'network_io', 'disk_io', 'request_rate']

for i in range(100):
    timestamp = now - timedelta(minutes=i)
    for metric_name in metrics:
        value = random.uniform(10, 100)
        metric = MetricData(
            metric_name=metric_name,
            value=value,
            timestamp=timestamp,
            labels=json.dumps({})
        )
        db.add(metric)

db.commit()
db.close()
print('Sample data created successfully')
"
cd ..

# Start backend
echo "🖥️ Starting backend server..."
cd backend
python -m app.main &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Build frontend
echo "🏗️ Building frontend..."
cd frontend
npm run build
cd ..

# Start frontend
echo "🌐 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "✅ Dashboard started successfully!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Press Ctrl+C to stop or run ./stop.sh"

# Keep script running
wait
