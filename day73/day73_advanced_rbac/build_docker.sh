#!/bin/bash

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 Building Advanced RBAC System (With Docker)"
echo "Project root: $PROJECT_ROOT"

# Check for duplicate services
if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps | grep -q "Up"; then
    echo "⚠️  Services already running. Stopping existing instances..."
    cd "$PROJECT_ROOT" || exit 1
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down
    sleep 2
fi

# Build and start services
cd "$PROJECT_ROOT" || exit 1
docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up --build -d

echo "✅ System is running!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "View logs: docker-compose -f $PROJECT_ROOT/docker-compose.yml logs -f"
echo "Stop: docker-compose -f $PROJECT_ROOT/docker-compose.yml down"
