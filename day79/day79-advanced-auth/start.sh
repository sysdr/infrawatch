#!/bin/bash

echo "Starting Advanced Authentication System..."

# Start services without rebuilding
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "Services status:"
docker-compose ps

echo ""
echo "Services are running:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend UI: http://localhost:3000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: ./stop.sh"
