#!/bin/bash

echo "Starting Day 76: User Directory Features"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found. Please run this script from the project directory."
    exit 1
fi

# Start services using docker-compose
echo "Starting Docker services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 15

echo ""
echo "Services running:"
echo "- LDAP Server: ldap://localhost:389"
echo "- Backend API: http://localhost:8000"
echo "- Frontend Dashboard: http://localhost:3000"
echo "- API Documentation: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To view status: docker-compose ps"
