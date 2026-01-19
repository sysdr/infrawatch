#!/bin/bash

set -e

echo "=========================================="
echo "Security UI Features - Cleanup Script"
echo "=========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop local services
echo "Stopping local services..."
if [ -f stop.sh ]; then
    ./stop.sh 2>/dev/null || true
fi

# Stop Docker containers
echo "Stopping Docker containers..."
if [ -f docker/docker-compose.yml ]; then
    docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
fi

# Stop any security-related containers
echo "Stopping security-related containers..."
docker ps -a --filter "name=security" -q | xargs -r docker stop 2>/dev/null || true
docker ps -a --filter "name=security" -q | xargs -r docker rm 2>/dev/null || true

# Remove unused Docker resources
echo "Removing unused Docker resources..."
echo "  - Removing stopped containers..."
docker container prune -f 2>/dev/null || true

echo "  - Removing unused images..."
docker image prune -f 2>/dev/null || true

echo "  - Removing unused volumes..."
docker volume prune -f 2>/dev/null || true

echo "  - Removing unused networks..."
docker network prune -f 2>/dev/null || true

# Remove build artifacts and caches
echo ""
echo "Removing build artifacts and caches..."

# Remove node_modules
if [ -d "frontend/node_modules" ]; then
    echo "  - Removing frontend/node_modules..."
    rm -rf frontend/node_modules
fi

# Remove Python virtual environment
if [ -d "backend/venv" ]; then
    echo "  - Removing backend/venv..."
    rm -rf backend/venv
fi

# Remove pytest cache
if [ -d "backend/.pytest_cache" ]; then
    echo "  - Removing backend/.pytest_cache..."
    rm -rf backend/.pytest_cache
fi

# Remove __pycache__ directories
echo "  - Removing __pycache__ directories..."
find . -type d -name "__pycache__" -not -path "*/venv/*" -exec rm -rf {} + 2>/dev/null || true

# Remove .pyc files
echo "  - Removing .pyc files..."
find . -name "*.pyc" -not -path "*/venv/*" -delete 2>/dev/null || true

# Remove .pyo files
echo "  - Removing .pyo files..."
find . -name "*.pyo" -not -path "*/venv/*" -delete 2>/dev/null || true

# Remove Istio files (if any)
echo "  - Removing Istio files..."
find . -type f -name "*istio*" -o -name "*Istio*" 2>/dev/null | xargs -r rm -f || true
find . -type d -name "*istio*" -o -name "*Istio*" 2>/dev/null | xargs -r rm -rf || true

# Remove log files
echo "  - Removing log files..."
rm -f *.log backend/*.log frontend/*.log 2>/dev/null || true

# Remove PID files
echo "  - Removing PID files..."
rm -f *.pid backend/*.pid frontend/*.pid 2>/dev/null || true

# Remove build artifacts
echo "  - Removing build artifacts..."
rm -rf frontend/build 2>/dev/null || true
rm -rf backend/dist 2>/dev/null || true
rm -rf backend/build 2>/dev/null || true

# Remove coverage reports
echo "  - Removing coverage reports..."
rm -rf htmlcov 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf backend/.coverage 2>/dev/null || true
rm -rf backend/htmlcov 2>/dev/null || true

# Remove IDE files
echo "  - Removing IDE files..."
rm -rf .vscode .idea *.swp *.swo *~ 2>/dev/null || true

echo ""
echo "=========================================="
echo "Cleanup completed successfully!"
echo "=========================================="
echo ""
echo "Removed:"
echo "  - Docker containers and resources"
echo "  - node_modules"
echo "  - Python virtual environment (venv)"
echo "  - Python cache files (__pycache__, .pyc, .pyo)"
echo "  - Pytest cache"
echo "  - Log files"
echo "  - Build artifacts"
echo ""
