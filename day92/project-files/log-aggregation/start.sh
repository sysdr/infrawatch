#!/bin/bash

# Start Log Aggregation services (backend, shipper, frontend)
# Use after ./build.sh or when deps are already installed.
# Stop with ./stop.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "Starting Log Aggregation System"
echo "======================================"

# Check PostgreSQL
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL not running on localhost:5432. Start it first (e.g. docker start day92-pg)"
    exit 1
fi
echo "PostgreSQL OK"

# Check Redis
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "Redis not running on localhost:6379. Start it first."
    exit 1
fi
echo "Redis OK"

# Activate venv if present
if [ -d venv ]; then
    source venv/bin/activate
fi

# Avoid duplicate backend on 8000
if lsof -i :8000 > /dev/null 2>&1; then
    echo "Port 8000 in use (backend may already be running). Skipping backend start."
else
    echo "Starting backend..."
    (cd "$SCRIPT_DIR/backend" && python main.py >> "$SCRIPT_DIR/backend.log" 2>&1) &
    echo $! > "$SCRIPT_DIR/.backend.pid"
    sleep 3
fi

# Avoid duplicate shipper
if [ -f .shipper.pid ] && kill -0 "$(cat .shipper.pid)" 2>/dev/null; then
    echo "Shipper already running. Skipping."
else
    echo "Starting log shipper..."
    (cd "$SCRIPT_DIR/shipper" && python shipper.py >> "$SCRIPT_DIR/shipper.log" 2>&1) &
    echo $! > "$SCRIPT_DIR/.shipper.pid"
fi

# Avoid duplicate frontend on 3000
if lsof -i :3000 > /dev/null 2>&1; then
    echo "Port 3000 in use (frontend may already be running). Skipping frontend start."
else
    echo "Starting frontend..."
    (cd "$SCRIPT_DIR/frontend" && PORT=3000 HOST=0.0.0.0 npm start >> "$SCRIPT_DIR/frontend.log" 2>&1) &
    echo $! > "$SCRIPT_DIR/.frontend.pid"
fi

echo ""
echo "======================================"
echo "Services started"
echo "======================================"
echo "Backend API: http://localhost:8000"
echo "API Docs:   http://localhost:8000/docs"
echo "Frontend:   http://localhost:3000"
echo ""
echo "Stop with: ./stop.sh"
