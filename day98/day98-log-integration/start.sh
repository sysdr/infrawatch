#!/bin/bash

set -e

echo "🚀 Starting Day 98: Log Management Integration"
echo "================================================"

if command -v docker &> /dev/null; then
    USE_DOCKER=true
    echo "✅ Docker detected"
else
    USE_DOCKER=false
    echo "⚠️  Docker not detected, using local setup"
fi

if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "🐳 Starting Docker services..."
    docker-compose up -d || true

    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 15

    echo ""
    echo "🔍 Service status:"
    docker-compose ps

    if ! docker-compose ps | grep -q "log-api.*Up"; then
        echo ""
        echo "⚠️  log-api may still be starting (waiting for Elasticsearch). Retrying in 30s..."
        sleep 30
        docker-compose up -d log-api 2>/dev/null || true
    fi
else
    echo ""
    echo "🚀 Starting local services..."

    if [ -f backend.pid ]; then
        echo "⚠️  Backend may already be running (backend.pid exists)"
    else
        cd backend
        source venv/bin/activate 2>/dev/null || { echo "❌ Run ./build.sh first to create venv"; exit 1; }

        echo "🚀 Starting backend API..."
        uvicorn main:app --host 0.0.0.0 --port 8000 &
        echo $! > ../backend.pid

        echo "🔄 Starting bulk indexer worker..."
        python workers/bulk_indexer.py &
        echo $! >> ../backend.pid

        echo "🗂️  Starting retention worker..."
        python workers/retention_worker.py &
        echo $! >> ../backend.pid

        echo "🔒 Starting security correlation worker..."
        python workers/security_correlation.py &
        echo $! >> ../backend.pid

        cd ..
        sleep 3
    fi
fi

echo ""
echo "🎨 Starting frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies (run ./build.sh for full setup)..."
    npm install --silent
fi

echo "🚀 Starting frontend dev server..."
HOST=0.0.0.0 PORT=3000 nohup npx react-scripts start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
disown $FRONTEND_PID 2>/dev/null || true

echo "   (Frontend compiling... check frontend.log for progress. May take 1-2 min.)"
cd ..

echo ""
echo "✅ Start complete!"
echo ""
echo "================================================"
echo "🎉 Day 98: Log Management Integration is running!"
echo "================================================"
echo ""
echo "📊 Access the application:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🛑 To stop: ./stop.sh"
echo ""
