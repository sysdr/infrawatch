#!/bin/bash
# Cleanup: stop all services, Docker resources, and remove generated/cache files

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Stopping application services ==="
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "http.server 3000" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
sleep 2

echo "=== Stopping Docker containers ==="
docker compose down 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true

echo "=== Removing unused Docker resources ==="
docker container prune -f
docker image prune -af
docker volume prune -f
docker network prune -f
docker system prune -af --volumes 2>/dev/null || true

echo "=== Removing node_modules, venv, cache ==="
rm -rf log-management-ui-app/frontend/node_modules
rm -rf log-management-ui-app/backend/venv
rm -rf log-management-ui-app/.pytest_cache
find log-management-ui-app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find log-management-ui-app -name "*.pyc" -delete 2>/dev/null || true

echo "=== Removing Istio files (if any) ==="
find . -path "*istio*" -type f 2>/dev/null | xargs rm -f 2>/dev/null || true
find . -path "*istio*" -type d 2>/dev/null | xargs rm -rf 2>/dev/null || true

echo "=== Cleanup complete ==="
