#!/bin/bash

# Infrastructure UI - Cleanup Script
# This script stops all services, Docker containers, and removes generated files

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "======================================"
echo "Infrastructure UI - Cleanup Script"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop services
echo -e "${YELLOW}Stopping services...${NC}"
./stop.sh 2>/dev/null || true

# Kill any remaining processes
echo -e "${YELLOW}Killing remaining processes...${NC}"
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "vite.*5173" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
sleep 2

# Stop and remove Docker containers
echo -e "${YELLOW}Stopping Docker containers...${NC}"
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose down -v 2>/dev/null || true
    echo -e "${GREEN}✓ Docker containers stopped${NC}"
fi

# Remove Docker resources
echo -e "${YELLOW}Cleaning up Docker resources...${NC}"
if command -v docker >/dev/null 2>&1; then
    # Remove stopped containers
    docker container prune -f 2>/dev/null || true
    
    # Remove unused images
    docker image prune -f 2>/dev/null || true
    
    # Remove unused volumes
    docker volume prune -f 2>/dev/null || true
    
    # Remove unused networks
    docker network prune -f 2>/dev/null || true
    
    echo -e "${GREEN}✓ Docker resources cleaned${NC}"
fi

# Remove node_modules
echo -e "${YELLOW}Removing node_modules...${NC}"
if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
    echo -e "${GREEN}✓ Removed frontend/node_modules${NC}"
fi

# Remove venv
echo -e "${YELLOW}Removing Python virtual environments...${NC}"
if [ -d "backend/venv" ]; then
    rm -rf backend/venv
    echo -e "${GREEN}✓ Removed backend/venv${NC}"
fi

# Remove .pytest_cache
echo -e "${YELLOW}Removing pytest cache...${NC}"
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Removed .pytest_cache directories${NC}"

# Remove __pycache__ and .pyc files
echo -e "${YELLOW}Removing Python cache files...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Removed Python cache files${NC}"

# Remove Istio files (if any)
echo -e "${YELLOW}Removing Istio files...${NC}"
find . -type d -name "*istio*" -o -name "*Istio*" 2>/dev/null | while read dir; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo -e "${GREEN}✓ Removed $dir${NC}"
    fi
done
find . -type f -name "*istio*" -o -name "*Istio*" 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "${GREEN}✓ Removed $file${NC}"
    fi
done

# Remove PID files
echo -e "${YELLOW}Removing PID files...${NC}"
rm -f .backend.pid .frontend.pid 2>/dev/null || true
echo -e "${GREEN}✓ Removed PID files${NC}"

# Remove log files
echo -e "${YELLOW}Removing log files...${NC}"
rm -f /tmp/backend.log /tmp/frontend.log /tmp/frontend_*.log 2>/dev/null || true
echo -e "${GREEN}✓ Removed log files${NC}"

# Remove package lock files (optional - comment out if you want to keep them)
# echo -e "${YELLOW}Removing package lock files...${NC}"
# rm -f frontend/package-lock.json 2>/dev/null || true

# Remove build artifacts
echo -e "${YELLOW}Removing build artifacts...${NC}"
rm -rf frontend/dist 2>/dev/null || true
rm -rf frontend/.vite 2>/dev/null || true
rm -rf backend/__pycache__ 2>/dev/null || true
echo -e "${GREEN}✓ Removed build artifacts${NC}"

echo ""
echo -e "${GREEN}======================================"
echo -e "Cleanup Complete!${NC}"
echo -e "${GREEN}======================================"
echo ""
echo "Removed:"
echo "  - node_modules"
echo "  - venv"
echo "  - .pytest_cache"
echo "  - __pycache__ and .pyc files"
echo "  - Istio files (if any)"
echo "  - Docker containers and resources"
echo "  - PID and log files"
echo ""
echo "To start fresh:"
echo "  ./build.sh"
echo ""
