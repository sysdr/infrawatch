#!/bin/bash

echo "=========================================="
echo "Building Report Templates System"
echo "=========================================="

# Check if Docker is requested
USE_DOCKER=${1:-"local"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo "Starting services with Docker..."
    cd docker
    docker-compose up -d
    cd ..
    sleep 5
else
    echo "Setting up local environment..."
    
    # Start PostgreSQL
    echo "Starting PostgreSQL..."
    docker run -d --name reports-postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=reports_db \
        -p 5432:5432 \
        postgres:15
    
    # Start Redis
    echo "Starting Redis..."
    docker run -d --name reports-redis \
        -p 6379:6379 \
        redis:7
    
    sleep 5
fi

# Backend setup
echo "Setting up backend..."
cd backend

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -c "from app.database import init_db; init_db()"

# Run tests
echo "Running tests..."
pytest tests/ -v

# Start backend services
echo "Starting API server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "Starting scheduler..."
python scheduler.py &
SCHEDULER_PID=$!

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend

npm install

echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Save PIDs
echo $API_PID > .api.pid
echo $SCHEDULER_PID > .scheduler.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo "API Server: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Run ./stop.sh to stop all services"
