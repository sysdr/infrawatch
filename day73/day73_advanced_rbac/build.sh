#!/bin/bash

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🚀 Building Advanced RBAC System (Without Docker)"
echo "Project root: $PROJECT_ROOT"

# Check for duplicate services
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "⚠️  Backend service already running. Stopping existing instance..."
    pkill -f "uvicorn app.main:app"
    sleep 2
fi

if pgrep -f "react-scripts start" > /dev/null; then
    echo "⚠️  Frontend service already running. Stopping existing instance..."
    pkill -f "react-scripts start"
    sleep 2
fi

# Setup Backend
echo "📦 Setting up backend..."
cd "$BACKEND_DIR" || exit 1

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source "$BACKEND_DIR/venv/bin/activate"

# Install dependencies
pip install -r "$BACKEND_DIR/requirements.txt"

# Setup PostgreSQL (assumes PostgreSQL is installed)
# Use environment variables if set, otherwise use defaults
export DATABASE_URL="${DATABASE_URL:-postgresql://rbac_user:rbac_pass@localhost:5432/rbac_db}"
export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"

# Note: You need PostgreSQL and Redis running locally
echo "⚠️  Ensure PostgreSQL and Redis are running:"
echo "   PostgreSQL: createdb rbac_db"
echo "   Redis: redis-server"

# Start backend
echo "🔥 Starting backend on port 8000..."
cd "$BACKEND_DIR" || exit 1
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Setup Frontend
echo "📦 Setting up frontend..."
cd "$FRONTEND_DIR" || exit 1

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    npm install
fi

# Start frontend
echo "🎨 Starting frontend on port 3000..."
cd "$FRONTEND_DIR" || exit 1
npm start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

cd "$PROJECT_ROOT" || exit 1

echo "✅ System is running!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
wait
