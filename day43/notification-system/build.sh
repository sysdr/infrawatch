#!/bin/bash

echo "🏗️  Building Notification System"

# Backend setup
echo "📦 Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Starting backend server..."
python app/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Frontend setup
echo "📦 Setting up React frontend..."
cd frontend
npm install

echo "🚀 Starting frontend server..."
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

# Save PIDs for stop script
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

echo ""
echo "🧪 Testing notification channels..."
sleep 10

# Test notifications
echo "📧 Testing email channel..."
curl -X POST "http://localhost:8000/notifications" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Email Notification",
    "message": "This is a test email from the notification system",
    "channel": "email",
    "recipient": "test@example.com",
    "priority": "medium"
  }'

echo ""
echo "📱 Testing SMS channel..."
curl -X POST "http://localhost:8000/notifications" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test SMS",
    "message": "This is a test SMS",
    "channel": "sms", 
    "recipient": "+1234567890",
    "priority": "high"
  }'

echo ""
echo "💬 Testing Slack channel..."
curl -X POST "http://localhost:8000/notifications" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Slack Notification",
    "message": "This is a test Slack message",
    "channel": "slack",
    "recipient": "#general",
    "priority": "medium"
  }'

echo ""
echo "✅ Build complete!"
echo "Open http://localhost:3000 to access the dashboard"

# Make scripts executable
chmod +x build.sh stop.sh docker_demo.sh

wait
