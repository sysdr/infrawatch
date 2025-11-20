#!/bin/bash
set -e

echo "=========================================="
echo "Day 54: Real-time Testing - Build & Run"
echo "=========================================="

cd "$(dirname "$0")"

print_usage() {
    echo "Usage: ./build.sh [--docker] [--skip-tests] [--fast]"
    echo ""
    echo "  --docker      Run using docker-compose"
    echo "  --skip-tests  Start services without executing pytest suites"
    echo "  --fast        Shortcut for '--skip-tests' with a helpful banner"
    echo ""
}

wait_for_backend_health() {
    local attempts=0
    local max_attempts=10
    local sleep_seconds=1
    while true; do
        response=$(curl -s http://localhost:8000/health || true)
        if [ -n "$response" ]; then
            echo "$response" | python3 -m json.tool && return 0
        fi
        attempts=$((attempts + 1))
        if [ $attempts -ge $max_attempts ]; then
            echo "Backend health check failed after $attempts attempts."
            return 1
        fi
        echo "Waiting for backend health ($attempts/$max_attempts)..."
        sleep $sleep_seconds
    done
}

USE_DOCKER=false
SKIP_TESTS=false
FAST_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --fast)
            SKIP_TESTS=true
            FAST_MODE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

if [ "$FAST_MODE" = true ]; then
    echo "[Fast mode] Skipping automated test suites for quicker startup."
fi

if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "[Docker Mode]"
    echo "Building and starting services..."
    
    docker-compose up --build -d
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo ""
    echo "Services running:"
    echo "  - Backend: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo ""
    echo "Health check:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    
else
    echo ""
    echo "[Local Mode]"
    
    echo "Preparing Python environment..."
    if [ ! -d venv ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    else
        echo "Reusing existing virtual environment."
    fi
    source venv/bin/activate
    
    REQ_HASH=$(sha256sum backend/requirements.txt | cut -d ' ' -f1)
    REQ_HASH_FILE="venv/.requirements_hash"
    if [ ! -f "$REQ_HASH_FILE" ] || [ "$REQ_HASH" != "$(cat "$REQ_HASH_FILE" 2>/dev/null)" ]; then
        echo "Installing backend dependencies..."
        pip install -r backend/requirements.txt
        echo "$REQ_HASH" > "$REQ_HASH_FILE"
    else
        echo "Backend dependencies unchanged; skipping pip install."
    fi
    
    echo "Starting backend server..."
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    echo "Waiting for backend to start..."
    sleep 2
    
    echo "Backend health check:"
    wait_for_backend_health
    
    echo ""
    echo "Preparing frontend..."
    cd frontend
    LOCK_HASH_FILE=".npm_hash"
    if [ -f package-lock.json ]; then
        LOCK_HASH=$(sha256sum package-lock.json | cut -d ' ' -f1)
    else
        LOCK_HASH=""
    fi
    
    if [ ! -d node_modules ] || [ -n "$LOCK_HASH" -a "$LOCK_HASH" != "$(cat "$LOCK_HASH_FILE" 2>/dev/null)" ]; then
        echo "Installing frontend dependencies..."
        npm install
        if [ -n "$LOCK_HASH" ]; then
            echo "$LOCK_HASH" > "$LOCK_HASH_FILE"
        fi
    else
        echo "Frontend dependencies unchanged; skipping npm install."
    fi
    
    echo "Starting frontend..."
    PORT=3000 npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo ""
    echo "Services running:"
    echo "  - Backend: http://localhost:8000 (PID: $BACKEND_PID)"
    echo "  - Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
fi

if [ "$SKIP_TESTS" = false ]; then
    echo ""
    echo "=========================================="
    echo "Running Unit Tests"
    echo "=========================================="
    
    if [ "$USE_DOCKER" = true ]; then
        docker-compose exec -T backend pytest tests/unit -v
    else
        source venv/bin/activate
        cd backend
        python -m pytest ../tests/unit -v
        cd ..
    fi
    
    echo ""
    echo "=========================================="
    echo "Running Integration Tests"
    echo "=========================================="
    
    if [ "$USE_DOCKER" = true ]; then
        docker-compose exec -T backend pytest tests/integration -v
    else
        source venv/bin/activate
        cd backend
        python -m pytest ../tests/integration -v
        cd ..
    fi
    
    echo ""
    echo "=========================================="
    echo "Running Load Tests"
    echo "=========================================="
    
    if [ "$USE_DOCKER" = true ]; then
        docker-compose exec -T backend pytest tests/load -v
    else
        source venv/bin/activate
        cd backend
        python -m pytest ../tests/load -v
        cd ..
    fi
    
    echo ""
    echo "=========================================="
    echo "Running Chaos Tests"
    echo "=========================================="
    
    if [ "$USE_DOCKER" = true ]; then
        docker-compose exec -T backend pytest tests/chaos -v
    else
        source venv/bin/activate
        cd backend
        python -m pytest ../tests/chaos -v
        cd ..
    fi
    
    echo ""
    echo "=========================================="
    echo "Running Full Test Suite"
    echo "=========================================="
    
    if [ "$USE_DOCKER" = true ]; then
        docker-compose exec -T backend python run_tests.py
    else
        source venv/bin/activate
        cd backend
        python run_tests.py
        cd ..
    fi
else
    echo ""
    echo "[Info] Automated tests skipped (--skip-tests)."
fi

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo ""
echo "Dashboard: http://localhost:3000"
echo "API Docs:  http://localhost:8000/docs"
echo "Metrics:   http://localhost:8000/api/metrics"
echo ""
echo "Test results saved to: reports/test_results.json"
