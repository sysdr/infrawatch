#!/bin/bash
# Stop containers, remove Docker resources, and clean project artifacts

set +e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Day 108 - Cleanup Script"
echo "=========================================="

# 1. Stop local services (ports 8000, 3000)
echo ""
echo "Stopping local services..."
for port in 8000 3000; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$PID" ]; then
        kill $PID 2>/dev/null && echo "  Stopped process on port $port" || true
    fi
done
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
sleep 2

# 2. Stop Docker containers and remove unused resources
echo ""
echo "Stopping Docker containers..."
docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true
CONTAINERS=$(docker ps -q 2>/dev/null)
[ -n "$CONTAINERS" ] && docker stop $CONTAINERS 2>/dev/null || true

echo "Removing unused Docker resources..."
docker container prune -f 2>/dev/null || true
docker image prune -f 2>/dev/null || true
docker volume prune -f 2>/dev/null || true
docker network prune -f 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# 3. Remove project artifacts
echo ""
echo "Removing project artifacts..."

[ -d "frontend/node_modules" ] && rm -rf frontend/node_modules && echo "  Removed frontend/node_modules"
[ -d "backend/venv" ] && rm -rf backend/venv && echo "  Removed backend/venv"
[ -d "backend/.pytest_cache" ] && rm -rf backend/.pytest_cache && echo "  Removed backend/.pytest_cache"

echo "  Removing .pyc and __pycache__..."
find "$SCRIPT_DIR" -type d -name "__pycache__" 2>/dev/null | while read -r d; do rm -rf "$d" 2>/dev/null; done || true
find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "  Removing Istio files (if any)..."
find "$SCRIPT_DIR" -path "*istio*" -not -path "*/node_modules/*" -not -path "*/venv/*" 2>/dev/null | head -100 | while read -r f; do rm -rf "$f" 2>/dev/null; done || true

# Remove PID files if present
rm -f .backend.pid .frontend.pid 2>/dev/null || true

echo ""
echo "=========================================="
echo "Cleanup complete."
echo "=========================================="
