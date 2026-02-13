#!/bin/bash
# Day 106 ML Pipeline - Cleanup script
# Stops containers, removes unused Docker resources, and cleans build artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Day 106 ML Pipeline - Cleanup"
echo "========================================="

# 1. Stop local processes
echo "Stopping local processes..."
pkill -f "uvicorn app.main" 2>/dev/null && echo "  Backend stopped" || true
pkill -f "vite --port 3106" 2>/dev/null && echo "  Frontend stopped" || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 1

# 2. Stop and remove Docker containers (project-specific)
echo "Stopping Docker containers..."
if [ -f docker-compose.yml ]; then
  docker compose down --remove-orphans 2>/dev/null && echo "  Docker Compose services stopped" || true
fi

# 3. Stop any running containers on project ports
docker ps -q --filter "publish=8106" 2>/dev/null | xargs -r docker stop 2>/dev/null || true
docker ps -q --filter "publish=3106" 2>/dev/null | xargs -r docker stop 2>/dev/null || true

# 4. Remove unused Docker resources
echo "Removing unused Docker resources..."
docker container prune -f 2>/dev/null && echo "  Containers pruned" || true
docker image prune -af 2>/dev/null && echo "  Images pruned" || true
docker volume prune -f 2>/dev/null && echo "  Volumes pruned" || true
docker network prune -f 2>/dev/null && echo "  Networks pruned" || true
docker system prune -af 2>/dev/null && echo "  System pruned" || true

# 5. Remove build artifacts
echo "Removing build artifacts..."
rm -rf frontend/node_modules 2>/dev/null && echo "  Removed node_modules" || true
rm -rf venv 2>/dev/null && echo "  Removed venv" || true
rm -rf frontend/dist 2>/dev/null && echo "  Removed frontend/dist" || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".eggs" -exec rm -rf {} + 2>/dev/null || true

# 6. Remove Istio-related files/dirs (if any)
echo "Removing Istio files..."
find . -iname "*istio*" -type f -delete 2>/dev/null || true
find . -type d -iname "*istio*" -exec rm -rf {} + 2>/dev/null || true

# 7. Remove database files (optional - uncomment if desired)
# rm -f backend/*.db 2>/dev/null || true

echo ""
echo "========================================="
echo "Cleanup complete."
echo "========================================="
