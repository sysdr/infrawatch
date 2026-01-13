#!/bin/bash

# Cleanup script for Security Assessment Platform
# Stops all containers and removes unused Docker resources

set -e

echo "================================"
echo "Security Assessment Platform Cleanup"
echo "================================"

# Stop all running containers
echo "Stopping Docker containers..."
docker ps -q | xargs -r docker stop 2>/dev/null || true

# Remove all containers
echo "Removing Docker containers..."
docker ps -a -q | xargs -r docker rm 2>/dev/null || true

# Remove unused images
echo "Removing unused Docker images..."
docker image prune -af 2>/dev/null || true

# Remove unused volumes
echo "Removing unused Docker volumes..."
docker volume prune -f 2>/dev/null || true

# Remove unused networks
echo "Removing unused Docker networks..."
docker network prune -f 2>/dev/null || true

# Stop docker-compose services if docker-compose.yml exists
if [ -f "docker-compose.yml" ]; then
    echo "Stopping docker-compose services..."
    docker-compose down -v 2>/dev/null || true
fi

# Remove build cache
echo "Removing Docker build cache..."
docker builder prune -af 2>/dev/null || true

# Stop local services
echo "Stopping local services..."
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "node.*start" 2>/dev/null || true

# Remove PID files
echo "Cleaning up PID files..."
rm -f backend.pid frontend.pid 2>/dev/null || true

# Remove log files
echo "Cleaning up log files..."
rm -f /tmp/backend.log /tmp/frontend.log 2>/dev/null || true

# Remove temporary files
echo "Cleaning up temporary files..."
rm -rf /tmp/scan_target/* 2>/dev/null || true

echo ""
echo "================================"
echo "Cleanup completed successfully!"
echo "================================"
echo ""
echo "Removed:"
echo "  - Docker containers"
echo "  - Docker images"
echo "  - Docker volumes"
echo "  - Docker networks"
echo "  - Docker build cache"
echo "  - Local service processes"
echo "  - PID and log files"
echo ""
echo "To start fresh, run: ./start.sh"
