#!/bin/bash

echo "🐳 Building with Docker..."

cd docker
docker-compose down
docker-compose build
docker-compose up -d

echo "✅ Docker services started!"
echo "🌐 Frontend: http://localhost:3000"  
echo "🔗 Backend API: http://localhost:8000"

# Create test data
sleep 10
echo "🎯 Creating test alerts..."

curl -X POST "http://localhost:8000/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker Test Alert",
    "description": "Testing alert processing in Docker",
    "metric_name": "cpu_usage",
    "service_name": "docker-service",
    "current_value": 88.0,
    "threshold_value": 85.0
  }'

echo "🎉 Docker demo ready!"
echo "📝 Run: cd docker && docker-compose down"
