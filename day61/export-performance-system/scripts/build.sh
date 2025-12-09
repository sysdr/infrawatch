#!/bin/bash

set -e

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Building Export Performance System"
echo "=========================================="
echo "Project directory: $PROJECT_DIR"

MODE=${1:-local}

if [ "$MODE" = "docker" ]; then
    echo "Building with Docker..."
    cd "$PROJECT_DIR"
    docker-compose down -v
    docker-compose build
    docker-compose up -d
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo "Services started successfully!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Building locally..."
    
    # Backend
    cd "$PROJECT_DIR/backend"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd "$PROJECT_DIR"
    
    # Frontend
    cd "$PROJECT_DIR/frontend"
    npm install
    cd "$PROJECT_DIR"
    
    echo "Build completed!"
    echo "Run '$PROJECT_DIR/scripts/start.sh' to start services"
fi
