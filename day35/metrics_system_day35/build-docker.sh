#!/bin/bash

set -e

echo "🐳 Building Day 35 with Docker"
echo "=================================================="

echo "📦 Building Docker services..."
cd docker
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "🔍 Checking service health..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is ready"
else
    echo "❌ Backend not ready"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is ready"
else
    echo "❌ Frontend not ready"
fi

echo ""
echo "✅ DOCKER BUILD SUCCESSFUL!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop: docker-compose -f docker/docker-compose.yml down"
echo ""
