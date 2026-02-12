#!/bin/bash
# cleanup.sh - Stop containers and remove unused Docker resources, containers, and images.
# Also stops app services and removes local build/cache artifacts.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Cleanup: Stopping services and Docker"
echo "=========================================="

# Stop application services
if [ -f "$SCRIPT_DIR/automation_integration/stop.sh" ]; then
  "$SCRIPT_DIR/automation_integration/stop.sh" 2>/dev/null || true
fi
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "node.*react-scripts" 2>/dev/null || true
echo "App services stopped."

# Stop all running containers
echo "Stopping Docker containers..."
docker stop $(docker ps -q) 2>/dev/null || true
for f in "$SCRIPT_DIR/automation_integration/docker/docker-compose.yml" "$SCRIPT_DIR/docker-compose.yml" "$SCRIPT_DIR/automation_integration/docker-compose.yml"; do
  [ -f "$f" ] && docker compose -f "$f" down 2>/dev/null || true
done
docker compose down 2>/dev/null || true
echo "Containers stopped."

# Remove unused Docker resources
echo "Removing unused Docker resources..."
docker container prune -f
docker network prune -f
docker volume prune -f
docker image prune -a -f
docker system prune -a -f --volumes
echo "Docker cleanup done."

# Remove local build/cache artifacts (optional - uncomment to run)
echo "Removing node_modules, venv, .pytest_cache, .pyc, __pycache__..."
rm -rf "$SCRIPT_DIR/automation_integration/frontend/node_modules" 2>/dev/null || true
rm -rf "$SCRIPT_DIR/automation_integration/backend/venv" 2>/dev/null || true
find "$SCRIPT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null || true
# Istio-related files/dirs (if any)
find "$SCRIPT_DIR" -type d -iname "*istio*" 2>/dev/null | while read d; do [ -n "$d" ] && rm -rf "$d" 2>/dev/null; done || true
echo "Local artifacts removed."

echo "=========================================="
echo "Cleanup complete."
echo "=========================================="
