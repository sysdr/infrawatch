#!/bin/bash

# Cleanup script for Data Protection System
# Stops containers and removes unused Docker resources

set -e

echo "========================================="
echo "Data Protection System - Cleanup"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo -e "${YELLOW}Stopping all services...${NC}"

# Stop application services
if [ -f "$PROJECT_ROOT/stop.sh" ]; then
    bash "$PROJECT_ROOT/stop.sh"
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
sleep 2

echo -e "${YELLOW}Stopping Docker containers...${NC}"

# Stop docker-compose if exists
if [ -f "$PROJECT_ROOT/docker/docker-compose.yml" ]; then
    cd "$PROJECT_ROOT/docker"
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
    cd "$PROJECT_ROOT"
fi

# Stop all containers related to this project
docker ps -a --filter "name=dataprotection" --format "{{.ID}}" | xargs -r docker stop 2>/dev/null || true
docker ps -a --filter "name=dataprotection" --format "{{.ID}}" | xargs -r docker rm 2>/dev/null || true

echo -e "${YELLOW}Removing unused Docker resources...${NC}"

# Remove unused containers
docker container prune -f 2>/dev/null || true

# Remove unused images
docker image prune -f 2>/dev/null || true

# Remove unused volumes
docker volume prune -f 2>/dev/null || true

# Remove unused networks
docker network prune -f 2>/dev/null || true

# Remove all unused resources (containers, networks, images, build cache)
docker system prune -a -f --volumes 2>/dev/null || true

echo -e "${YELLOW}Cleaning up project files...${NC}"

# Remove node_modules
find "$PROJECT_ROOT" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true

# Remove venv
find "$PROJECT_ROOT" -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true

# Remove Python cache
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyd" -delete 2>/dev/null || true

# Remove Istio files
find "$PROJECT_ROOT" -type f -iname "*istio*" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type d -iname "*istio*" -exec rm -rf {} + 2>/dev/null || true

# Remove PID files
rm -f "$PROJECT_ROOT/.backend.pid" 2>/dev/null || true
rm -f "$PROJECT_ROOT/.frontend.pid" 2>/dev/null || true

# Remove log files
rm -f /tmp/backend.log /tmp/backend_*.log /tmp/frontend.log 2>/dev/null || true

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Removed:"
echo "  - Docker containers and unused resources"
echo "  - node_modules directories"
echo "  - Python virtual environments (venv)"
echo "  - Python cache files (__pycache__, .pyc, .pytest_cache)"
echo "  - Istio files"
echo "  - PID and log files"
echo ""
