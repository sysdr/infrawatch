#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Starting Log Search Engine"
echo "========================================="

# If no args and Docker is available, use Docker so Postgres/Redis/backend/frontend all start
if [ -z "$1" ] && command -v docker >/dev/null 2>&1 && [ -f docker-compose.yml ]; then
    echo "Using Docker (start Postgres, Redis, backend, frontend). Use ./start.sh --no-docker to run locally."
    exec "$SCRIPT_DIR/start.sh" --docker
fi

# Explicit no-docker: skip the auto-docker above (used when called with --no-docker)
if [ "$1" == "--no-docker" ]; then
    shift
fi

# Docker: start all services
if [ "$1" == "--docker" ]; then
    docker compose up -d postgres redis
    echo "Waiting for postgres and redis..."
    sleep 10
    docker compose up -d backend
    sleep 5
    docker compose exec -T backend python app/utils/data_generator.py 2>/dev/null || true
    docker compose up -d frontend
    echo "========================================="
    echo "Services are running!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "========================================="
    exit 0
fi

# No Docker: start backend and frontend (assume venv and npm deps already exist)
if [ -f backend.pid ] && kill -0 "$(cat backend.pid)" 2>/dev/null; then
    echo "Backend already running (PID $(cat backend.pid)). Use ./stop.sh first to restart."
else
    rm -f backend.pid
    cd "$SCRIPT_DIR/backend"
    if [ ! -d venv ]; then
        echo "Run ./build.sh first to create the backend venv."
        exit 1
    fi
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    echo $! > "$SCRIPT_DIR/backend.pid"
    cd "$SCRIPT_DIR"
    echo "Backend started (PID $(cat backend.pid))."
fi

if [ -f frontend.pid ] && kill -0 "$(cat frontend.pid)" 2>/dev/null; then
    echo "Frontend already running (PID $(cat frontend.pid)). Use ./stop.sh first to restart."
else
    rm -f frontend.pid
    cd "$SCRIPT_DIR/frontend"
    if [ ! -d node_modules ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    BROWSER=none npm start &
    echo $! > "$SCRIPT_DIR/frontend.pid"
    cd "$SCRIPT_DIR"
    echo "Frontend started (PID $(cat frontend.pid))."
fi

echo "========================================="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "========================================="
