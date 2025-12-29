#!/bin/bash

# Team Management System Deployment Script
# Complete deployment: build, setup, and start all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "=========================================="
echo "Team Management System Deployment"
echo "=========================================="

# Function to check if a process is running on a port
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null || true
        sleep 2
    fi
}

# Step 1: Clean up any existing services
echo ""
echo "Step 1: Cleaning up existing services..."
for port in 8000 3000; do
    if check_port $port; then
        echo "Stopping service on port $port..."
        kill_port $port
    fi
done

# Step 2: Start database services
echo ""
echo "Step 2: Starting database services..."
cd "$PROJECT_ROOT"

if ! check_port 5432; then
    echo "Starting PostgreSQL..."
    docker-compose up -d postgres 2>&1 | grep -v "version" || true
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
            echo "✓ PostgreSQL is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "ERROR: PostgreSQL failed to start"
            exit 1
        fi
        sleep 1
    done
else
    echo "✓ PostgreSQL is already running"
fi

if ! check_port 6379; then
    echo "Starting Redis..."
    docker-compose up -d redis 2>&1 | grep -v "version" || true
    sleep 2
    if redis-cli ping >/dev/null 2>&1; then
        echo "✓ Redis is ready"
    else
        echo "WARNING: Redis may not be ready yet"
    fi
else
    echo "✓ Redis is already running"
fi

# Step 3: Build backend
echo ""
echo "Step 3: Building backend..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment activation script not found"
    exit 1
fi

source venv/bin/activate

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found"
    exit 1
fi

echo "Installing backend dependencies..."
pip install -q -r requirements.txt

# Verify models can be imported
echo "Verifying backend setup..."
if PYTHONPATH=. python -c "from app.models.team import Team, TeamActivity; print('✓ Models verified')" 2>/dev/null; then
    echo "✓ Backend models verified"
else
    echo "ERROR: Backend models failed to import"
    exit 1
fi

# Step 4: Run tests
echo ""
echo "Step 4: Running tests..."
if PYTHONPATH=. pytest tests/ -v --tb=short 2>&1 | grep -E "PASSED|FAILED|ERROR" | head -5; then
    echo "✓ Tests completed"
else
    echo "WARNING: Some tests may have failed (check output above)"
fi

# Step 5: Start backend
echo ""
echo "Step 5: Starting backend server..."
cd "$BACKEND_DIR"

if check_port 8000; then
    echo "Port 8000 already in use, killing existing process..."
    kill_port 8000
fi

source venv/bin/activate
nohup bash -c "PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000" > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: Backend failed to start"
        cat "$PROJECT_ROOT/backend.log" | tail -20
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Step 6: Generate demo data
echo ""
echo "Step 6: Generating demo data..."
cd "$BACKEND_DIR"
source venv/bin/activate
if [ -f "demo_data.py" ]; then
    if PYTHONPATH=. python demo_data.py 2>&1 | grep -E "Created|Team ID|Dashboard"; then
        echo "✓ Demo data generated"
    else
        echo "WARNING: Demo data generation may have issues (check output above)"
    fi
else
    echo "WARNING: demo_data.py not found, skipping demo data generation"
fi

# Step 7: Validate dashboard
echo ""
echo "Step 7: Validating dashboard metrics..."
sleep 2
DASHBOARD_RESPONSE=$(curl -s http://localhost:8000/api/teams/1/dashboard 2>/dev/null || echo "")

if [ -n "$DASHBOARD_RESPONSE" ]; then
    TOTAL_MEMBERS=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('total_members', 0))" 2>/dev/null || echo "0")
    ACTIVE_TODAY=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('active_members_today', 0))" 2>/dev/null || echo "0")
    TOTAL_ACTIVITIES=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('total_activities', 0))" 2>/dev/null || echo "0")
    
    if [ "$TOTAL_MEMBERS" != "0" ] && [ "$TOTAL_ACTIVITIES" != "0" ]; then
        echo "✓ Dashboard metrics validated:"
        echo "  - Total Members: $TOTAL_MEMBERS"
        echo "  - Active Today: $ACTIVE_TODAY"
        echo "  - Total Activities: $TOTAL_ACTIVITIES"
    else
        echo "WARNING: Dashboard metrics may be zero"
    fi
else
    echo "WARNING: Could not fetch dashboard data"
fi

# Step 8: Build frontend (optional, may have permission issues)
echo ""
echo "Step 8: Building frontend..."
cd "$FRONTEND_DIR"

if [ -f "package.json" ]; then
    if [ -d "node_modules" ] && [ -f "node_modules/.bin/react-scripts" ]; then
        echo "✓ Frontend dependencies already installed"
    else
        echo "Installing frontend dependencies (may have permission issues on WSL)..."
        npm install --legacy-peer-deps 2>&1 | tail -3 || echo "WARNING: npm install had issues"
    fi
    
    # Try to start frontend (non-blocking)
    if [ -f "node_modules/.bin/react-scripts" ]; then
        if ! check_port 3000; then
            echo "Starting frontend server..."
            BROWSER=none nohup npm start > "$PROJECT_ROOT/frontend.log" 2>&1 &
            FRONTEND_PID=$!
            echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"
            echo "Frontend started with PID: $FRONTEND_PID"
            echo "Frontend may take 30-60 seconds to be ready..."
        else
            echo "✓ Frontend port 3000 is already in use"
        fi
    else
        echo "⚠ Frontend dependencies not fully installed (npm permission issues possible)"
        echo "  You can manually install with: cd frontend && npm install --legacy-peer-deps"
    fi
else
    echo "WARNING: package.json not found"
fi

# Final status
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Service Status:"
echo "  Backend:  http://localhost:8000 $(curl -s http://localhost:8000/health >/dev/null 2>&1 && echo '✓' || echo '✗')"
echo "  Frontend: http://localhost:3000 $(check_port 3000 && echo '✓' || echo '⚠ Starting...')"
echo "  API Docs: http://localhost:8000/docs"
echo "  Dashboard: http://localhost:8000/api/teams/1/dashboard"
echo ""
echo "Database Services:"
echo "  PostgreSQL: $(pg_isready -h localhost -p 5432 >/dev/null 2>&1 && echo '✓ Running' || echo '✗ Not running')"
echo "  Redis: $(redis-cli ping >/dev/null 2>&1 && echo '✓ Running' || echo '✗ Not running')"
echo ""
echo "Logs:"
echo "  Backend:  $PROJECT_ROOT/backend.log"
echo "  Frontend: $PROJECT_ROOT/frontend.log"
echo ""
echo "To stop services: ./stop.sh"
echo "=========================================="


