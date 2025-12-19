#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

case "$1" in
    setup)
        log_info "Setting up project..."
        
        # Backend setup
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
        
        # Frontend setup
        cd frontend
        npm install
        cd ..
        
        log_info "Setup complete!"
        ;;
        
    start)
        log_info "Starting services..."
        
        # Check if Redis is running
        REDIS_RUNNING=false
        if command -v redis-cli > /dev/null 2>&1 && redis-cli ping > /dev/null 2>&1; then
            REDIS_RUNNING=true
        elif docker ps --format '{{.Names}}' | grep -q redis-dashboard && docker exec redis-dashboard redis-cli ping > /dev/null 2>&1; then
            REDIS_RUNNING=true
        fi
        
        if [ "$REDIS_RUNNING" = false ]; then
            log_error "Redis is not running. Please start Redis first."
            exit 1
        fi
        
        # Start backend
        cd backend
        source venv/bin/activate
        uvicorn app.main:app --reload --port 8000 &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        echo $BACKEND_PID > backend.pid
        echo $FRONTEND_PID > frontend.pid
        
        log_info "Services started!"
        log_info "Backend: http://localhost:8000"
        log_info "Frontend: http://localhost:3000"
        ;;
        
    test-performance)
        log_info "Running performance tests..."
        
        cd backend
        source venv/bin/activate
        pytest tests/test_performance.py -v
        cd ..
        ;;
        
    stop)
        log_info "Stopping services..."
        
        if [ -f backend.pid ]; then
            kill $(cat backend.pid) 2>/dev/null || true
            rm backend.pid
        fi
        
        if [ -f frontend.pid ]; then
            kill $(cat frontend.pid) 2>/dev/null || true
            rm frontend.pid
        fi
        
        log_info "Services stopped"
        ;;
        
    *)
        echo "Usage: $0 {setup|start|test-performance|stop}"
        exit 1
        ;;
esac
