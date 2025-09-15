#!/bin/bash

set -e

echo "🐳 Building Task Orchestration System with Docker..."

# Build and start services
echo "🚀 Starting services with Docker Compose..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🧪 Running health checks..."
curl -f http://localhost:8000/api/v1/health || (echo "❌ Backend health check failed" && exit 1)

echo "✅ Services started successfully with Docker!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost:3000"  
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo ""
echo "🛑 To stop: docker-compose down"
