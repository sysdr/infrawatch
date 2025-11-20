#!/bin/bash

echo "Stopping services..."

cd "$(dirname "$0")"

# Stop Docker services if running
if docker-compose ps -q 2>/dev/null; then
    echo "Stopping Docker services..."
    docker-compose down
fi

# Stop local processes
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm .frontend.pid
fi

# Kill any remaining processes on ports
for port in 8000 3000; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill $pid 2>/dev/null
    fi
done

echo "All services stopped."
