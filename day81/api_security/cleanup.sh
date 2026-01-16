#!/bin/bash

# Cleanup script for API Security System
# Stops containers and removes unused Docker resources

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}API Security System - Cleanup Script${NC}"
echo -e "${BLUE}=====================================${NC}"

# Stop all services
echo -e "${YELLOW}Stopping all services...${NC}"
if [ -f "./stop.sh" ]; then
    ./stop.sh
else
    # Manual stop
    pkill -f "uvicorn app.main" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
fi

# Stop Docker containers
echo -e "${YELLOW}Stopping Docker containers...${NC}"
if [ -f "docker/docker-compose.yml" ]; then
    cd docker
    docker-compose down -v 2>/dev/null || true
    cd ..
fi

# Remove project-specific containers
echo -e "${YELLOW}Removing project containers...${NC}"
docker ps -a --filter "name=api_security" --filter "name=postgres" --filter "name=redis" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true

# Remove unused Docker resources
echo -e "${YELLOW}Cleaning up Docker resources...${NC}"

# Remove stopped containers
echo -e "${BLUE}  Removing stopped containers...${NC}"
docker container prune -f 2>/dev/null || true

# Remove unused networks
echo -e "${BLUE}  Removing unused networks...${NC}"
docker network prune -f 2>/dev/null || true

# Remove unused volumes
echo -e "${BLUE}  Removing unused volumes...${NC}"
docker volume prune -f 2>/dev/null || true

# Remove unused images (optional - be careful with this)
read -p "Remove unused Docker images? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}  Removing unused images...${NC}"
    docker image prune -f 2>/dev/null || true
fi

# Remove build cache (optional)
read -p "Remove Docker build cache? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}  Removing build cache...${NC}"
    docker builder prune -f 2>/dev/null || true
fi

# Clean up project files
echo -e "${YELLOW}Cleaning up project files...${NC}"

# Remove Python cache
echo -e "${BLUE}  Removing Python cache files...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove virtual environments
echo -e "${BLUE}  Removing virtual environments...${NC}"
find . -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true

# Remove node_modules
echo -e "${BLUE}  Removing node_modules...${NC}"
find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true

# Remove log files
echo -e "${BLUE}  Removing log files...${NC}"
find . -type f -name "*.log" -delete 2>/dev/null || true
find . -type f -name "*.pid" -delete 2>/dev/null || true

# Remove Istio files if any
echo -e "${BLUE}  Removing Istio files...${NC}"
find . -type d -name "istio" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*istio*" -delete 2>/dev/null || true

# Remove temporary files
echo -e "${BLUE}  Removing temporary files...${NC}"
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.swp" -delete 2>/dev/null || true
find . -type f -name "*.swo" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✓ Cleanup completed successfully!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}Removed:${NC}"
echo -e "  - Docker containers and volumes"
echo -e "  - Python cache files (__pycache__, *.pyc)"
echo -e "  - Virtual environments (venv)"
echo -e "  - Node modules (node_modules)"
echo -e "  - Log files (*.log, *.pid)"
echo -e "  - Istio files (if any)"
echo -e "  - Temporary files"
echo ""
