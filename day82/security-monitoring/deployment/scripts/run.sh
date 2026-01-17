#!/bin/bash

echo "Starting Security Monitoring System..."

# Start services
docker-compose -f deployment/docker/docker-compose.yml up -d

echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "========================================="
echo "Security Monitoring System is running!"
echo "========================================="
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Testing endpoints:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "Simulating security events..."
curl -X POST "http://localhost:8000/api/events/simulate?event_type=failed_login&count=10"
sleep 2
curl -X POST "http://localhost:8000/api/events/simulate?event_type=unusual_access&count=5"

echo ""
echo "View the dashboard at: http://localhost:3000"
