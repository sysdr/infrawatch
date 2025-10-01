#!/bin/bash

echo "🛑 Stopping Alert Evaluation Engine"
echo "================================="

# Kill backend process
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🐍 Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm backend.pid
fi

# Kill frontend process
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚛️  Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm frontend.pid
fi

# Stop Docker containers
if command -v docker >/dev/null 2>&1; then
    echo "🐳 Stopping infrastructure services..."
    docker stop alert-redis alert-postgres 2>/dev/null || true
    docker rm alert-redis alert-postgres 2>/dev/null || true
fi

echo "✅ Application stopped"
