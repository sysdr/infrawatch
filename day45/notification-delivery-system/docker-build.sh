#!/bin/bash

echo "🐳 Building with Docker..."

cd docker
docker-compose up --build -d

echo "✅ Docker containers started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: docker-compose down"
