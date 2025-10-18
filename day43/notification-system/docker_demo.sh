#!/bin/bash

echo "🐳 Starting Docker Demo..."

# Build and start services
echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Test the API
echo "🧪 Testing notification system..."

# Test email notification
echo "📧 Testing email notification..."
curl -X POST "http://localhost:8000/notifications" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker Test Email",
    "message": "This email was sent from the dockerized notification system",
    "channel": "email",
    "recipient": "test@example.com",
    "priority": "medium"
  }'

echo ""
echo "📱 Testing SMS notification..."
curl -X POST "http://localhost:8000/notifications" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker Test SMS",
    "message": "This SMS was sent from Docker",
    "channel": "sms",
    "recipient": "+1234567890",
    "priority": "high"
  }'

echo ""
echo "💬 Testing Slack notification..."
curl -X POST "http://localhost:8000/notifications" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker Test Slack",
    "message": "This Slack message was sent from Docker",
    "channel": "slack",
    "recipient": "#general",
    "priority": "medium"
  }'

echo ""
echo "📊 Checking statistics..."
curl -s "http://localhost:8000/stats" | python3 -m json.tool

echo ""
echo "✅ Docker demo complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000" 
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop services: docker-compose down"
