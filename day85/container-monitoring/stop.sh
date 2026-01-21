#!/bin/bash

echo "Stopping Container Monitoring System..."

# Stop Docker containers
docker-compose -f docker/docker-compose.yml down

# Kill any running processes
pkill -f "uvicorn backend.app.main"
pkill -f "vite"

echo "All services stopped"
