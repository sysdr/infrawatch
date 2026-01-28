#!/bin/bash
#
# cleanup.sh - Stop containers and remove unused Docker resources, project artifacts
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Cleanup: Stopping services and Docker"
echo "========================================"

# Stop application services (log-aggregation)
if [ -f log-aggregation/stop.sh ]; then
    (cd log-aggregation && ./stop.sh) 2>/dev/null || true
    (cd log-aggregation && ./stop.sh --docker) 2>/dev/null || true
fi

# Stop any Docker Compose from log-aggregation/docker
if [ -d log-aggregation/docker ]; then
    (cd log-aggregation/docker && docker compose down -v 2>/dev/null) || true
    (cd log-aggregation/docker && docker-compose down -v 2>/dev/null) || true
fi

# Stop all running containers
docker stop $(docker ps -q) 2>/dev/null || true

# Remove stopped containers
docker container prune -f

# Remove unused images (dangling)
docker image prune -f

# Remove unused images (all without containers)
# docker image prune -a -f   # uncomment for aggressive image cleanup

# Remove unused volumes
docker volume prune -f

# Remove unused networks
docker network prune -f

# Optional: full system prune (removes all unused data)
# docker system prune -a -f --volumes   # uncomment for full cleanup

echo "Docker cleanup done."

# Optional: remove project artifacts (node_modules, venv, caches)
REMOVE_ARTIFACTS="${REMOVE_ARTIFACTS:-}"
if [ "$1" = "--all" ] || [ "$REMOVE_ARTIFACTS" = "1" ]; then
    echo "Removing project artifacts..."
    for dir in log-aggregation/frontend/node_modules log-aggregation/venv; do
        [ -d "$dir" ] && rm -rf "$dir" && echo "  removed $dir"
    done
    [ -d log-aggregation/.pytest_cache ] && rm -rf log-aggregation/.pytest_cache
    find log-aggregation -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find log-aggregation -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find log-aggregation -name "*.pyc" -delete 2>/dev/null || true
    find . -maxdepth 4 -type d -iname "*istio*" 2>/dev/null | while read -r d; do [ -n "$d" ] && rm -rf "$d"; done
    find . -maxdepth 4 -type f -iname "*istio*" 2>/dev/null | while read -r f; do [ -n "$f" ] && rm -f "$f"; done
    echo "Artifacts cleanup done."
fi

echo "========================================"
echo "Cleanup finished."
echo "========================================"
echo "Usage:"
echo "  ./cleanup.sh           - Stop services and Docker only"
echo "  ./cleanup.sh --all     - Also remove node_modules, venv, .pytest_cache, .pyc, Istio"
