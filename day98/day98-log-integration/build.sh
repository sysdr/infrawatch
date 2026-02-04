#!/bin/bash

set -e

echo "🏗️  Building Day 98: Log Management Integration"
echo "================================================"

if [[ "$1" == "--no-docker" ]] || [[ "$1" == "--local" ]]; then
    USE_DOCKER=false
    echo "📌 Using local setup (Docker skipped)"
elif command -v docker &> /dev/null; then
    USE_DOCKER=true
    echo "✅ Docker detected"
else
    USE_DOCKER=false
    echo "⚠️  Docker not detected, using local setup"
fi

if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "📦 Building Docker images..."
    docker-compose build

    echo ""
    echo "🚀 Starting services with Docker..."
    docker-compose up -d

    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10

    echo ""
    echo "🔍 Checking service health..."
    docker-compose ps
else
    echo ""
    echo "📦 Setting up local environment..."

    echo "🔧 Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --quiet -r requirements.txt
    cd ..

    if command -v redis-server &> /dev/null; then
        echo "🔴 Starting Redis..."
        redis-server --daemonize yes --port 6379
    else
        echo "⚠️  Redis not found, please install Redis"
        exit 1
    fi

    if command -v elasticsearch &> /dev/null; then
        echo "🔍 Starting Elasticsearch..."
        elasticsearch -d
    else
        echo "⚠️  Elasticsearch not found, please install Elasticsearch"
        exit 1
    fi

    echo "⏳ Waiting for services..."
    sleep 5

    echo "🚀 Starting backend API..."
    cd backend
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid

    echo "🔄 Starting bulk indexer worker..."
    python workers/bulk_indexer.py &
    BULK_PID=$!
    echo $BULK_PID >> ../backend.pid

    echo "🗂️  Starting retention worker..."
    python workers/retention_worker.py &
    RETENTION_PID=$!
    echo $RETENTION_PID >> ../backend.pid

    echo "🔒 Starting security correlation worker..."
    python workers/security_correlation.py &
    SECURITY_PID=$!
    echo $SECURITY_PID >> ../backend.pid

    cd ..

    sleep 3
fi

echo ""
echo "🎨 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install --silent
fi

echo "🚀 Starting frontend..."
npm start &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid

cd ..

echo ""
echo "✅ Build complete!"
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
echo "🧪 Test the system:"
echo "   1. Generate test logs:"
echo "      python3 scripts/generate_test_logs.py 100 10"
echo ""
echo "   2. Simulate brute force attack:"
echo "      python3 scripts/simulate_brute_force.py testuser 10 5"
echo ""
echo "   3. View real-time logs in dashboard"
echo "   4. Search logs using the search interface"
echo "   5. Monitor security alerts"
echo ""
echo "🛑 To stop all services:"
echo "   ./stop.sh"
echo ""
