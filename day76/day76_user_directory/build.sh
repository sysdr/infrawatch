#!/bin/bash
set -e

echo "Building Day 76: User Directory Features"
echo "========================================"

# Option 1: Docker Build
if [ "$1" == "docker" ]; then
    echo "Building with Docker..."
    docker-compose up -d --build
    echo ""
    echo "Waiting for services to be ready..."
    sleep 15
    
    echo ""
    echo "Services running:"
    echo "- LDAP Server: ldap://localhost:389"
    echo "- Backend API: http://localhost:8000"
    echo "- Frontend Dashboard: http://localhost:3000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    exit 0
fi

# Option 2: Local Development
echo "Setting up local development environment..."

# Backend setup
cd backend
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting infrastructure services..."
cd ..
docker-compose up -d ldap redis postgres

echo "Waiting for services..."
sleep 10

echo "Running database migrations..."
cd backend
export DATABASE_URL="postgresql://userdir:userdir123@localhost:5432/userdir"
export REDIS_URL="redis://localhost:6379"
export LDAP_SERVER="ldap://localhost:389"
export LDAP_BASE_DN="dc=example,dc=com"
export LDAP_BIND_DN="cn=admin,dc=example,dc=com"
export LDAP_BIND_PASSWORD="admin"

python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

echo "Running backend tests..."
pytest tests/ -v

echo "Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 5

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "Services running:"
echo "- LDAP Server: ldap://localhost:389"
echo "- Backend API: http://localhost:8000"
echo "- Frontend Dashboard: http://localhost:3000"
echo "- API Documentation: http://localhost:8000/docs"
echo ""
echo "Demo Credentials:"
echo "LDAP Users:"
echo "  - john.doe / password123"
echo "  - jane.smith / password123"
echo "  - admin / admin123"
echo ""
echo "Press Ctrl+C to stop all services"
wait
