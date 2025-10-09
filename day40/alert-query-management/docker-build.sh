#!/bin/bash

echo "🐳 Starting Docker build and deployment..."

# Build and start with docker-compose
cd docker
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/health || echo "Backend health check failed"
curl -f http://localhost:3000 || echo "Frontend health check failed"

echo "✅ Docker deployment completed!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
