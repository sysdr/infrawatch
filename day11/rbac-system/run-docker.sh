#!/bin/bash

echo "🐳 Starting RBAC System with Docker..."

# Build and start services
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec app python scripts/init_db.py

echo "✅ RBAC System is running!"
echo "🌐 Web interface: http://localhost:8000"
echo "📖 API documentation: http://localhost:8000/docs"
echo "🔑 Default admin credentials: admin / admin123"

# Show logs
docker-compose logs -f app
