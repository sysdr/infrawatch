#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_info "Stopping all services..."

# Stop Docker containers
if [ -f docker-compose.yml ]; then
    docker-compose down
fi

# Stop local processes
pkill -f "uvicorn app.main:app" || true
pkill -f "vite" || true
pkill -f "node.*vite" || true

# Clean up PID files
rm -f backend.pid frontend.pid

log_info "All services stopped"
