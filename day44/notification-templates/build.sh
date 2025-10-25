#!/bin/bash

echo "🚀 Building Notification Templates System"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Docker detected - Building with Docker"
    
    # Backend Dockerfile
    cat > backend/Dockerfile << 'DOCKEREOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
DOCKEREOF

    # Frontend Dockerfile
    cat > frontend/Dockerfile << 'DOCKEREOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
DOCKEREOF

    # Docker Compose
    cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - ENV=development
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api
DOCKEREOF

    # Build and run with Docker
    docker-compose up --build -d
    
    echo "✅ Docker containers started"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    
else
    echo "📦 Docker not available - Building locally"
    
    # Backend setup
    echo "🐍 Setting up Python backend..."
    cd backend
    python -m venv venv
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    pip install -r requirements.txt
    
    # Start backend
    echo "🚀 Starting backend server..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # Frontend setup
    echo "⚛️ Setting up React frontend..."
    cd frontend
    npm install
    
    # Start frontend
    echo "🚀 Starting frontend server..."
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    echo "✅ Services started"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
fi

# Run tests
echo "🧪 Running tests..."
cd backend
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
elif [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
fi

pytest tests/ -v

echo "✅ Build complete!"
echo ""
echo "📋 Quick Start Guide:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Explore the template dashboard"
echo "3. Click 'Preview' on any template to see it rendered"
echo "4. Visit the Testing panel to run template tests"
echo "5. Use the API at http://localhost:8000/docs for integration"
