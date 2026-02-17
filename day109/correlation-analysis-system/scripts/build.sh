#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Building Correlation Analysis System"
echo "=========================================="

# Check if running with Docker flag
DOCKER_MODE=${1:-"no-docker"}

if [ "$DOCKER_MODE" = "docker" ]; then
    echo "Building with Docker..."
    cd "$PROJECT_ROOT/docker"
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo "Services started successfully!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Building without Docker..."
    
    # Backend setup
    echo "Setting up backend..."
    cd "$PROJECT_ROOT/backend"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Frontend setup
    echo "Setting up frontend..."
    cd "$PROJECT_ROOT/frontend"
    npm install
    
    echo "Build completed!"
    echo "Run '$PROJECT_ROOT/scripts/run.sh' to start the services"
fi
