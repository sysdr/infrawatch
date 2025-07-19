#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Auth Integration Services...${NC}"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Function to kill process on port
kill_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}🔄 Killing process on port $1...${NC}"
        lsof -ti:$1 | xargs kill -9
        sleep 2
    fi
}

# Check and kill existing processes
echo -e "${BLUE}🔍 Checking for existing processes...${NC}"
kill_port 8000  # Backend
kill_port 3000  # Frontend
kill_port 6379  # Redis

# Start Redis
echo -e "${BLUE}📦 Starting Redis...${NC}"
if ! command -v redis-server &> /dev/null; then
    echo -e "${RED}❌ Redis is not installed. Please install Redis first.${NC}"
    echo -e "${YELLOW}   On macOS: brew install redis${NC}"
    echo -e "${YELLOW}   On Ubuntu: sudo apt-get install redis-server${NC}"
    exit 1
fi

redis-server --daemonize yes
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Redis started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start Redis${NC}"
    exit 1
fi

# Wait for Redis to be ready
echo -e "${BLUE}⏳ Waiting for Redis to be ready...${NC}"
sleep 3

# Start Backend
echo -e "${BLUE}🐍 Starting FastAPI Backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating default .env...${NC}"
    cat > .env << EOF
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./auth_integration.db
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=["http://localhost:3000"]
EOF
    echo -e "${GREEN}✅ Created default .env file${NC}"
fi

# Start backend server
echo -e "${BLUE}🚀 Starting FastAPI server on port 8000...${NC}"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Backend started successfully${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

cd ..

# Start Frontend
echo -e "${BLUE}⚛️  Starting React Frontend...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
    npm install
fi

# Start frontend server
echo -e "${BLUE}🚀 Starting React development server on port 3000...${NC}"
npm start &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid

cd ..

# Wait for frontend to start
sleep 5

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ Frontend started successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may still be starting up...${NC}"
fi

echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo -e "${BLUE}📊 Service Status:${NC}"
echo -e "   ${GREEN}✅ Redis:${NC} localhost:6379"
echo -e "   ${GREEN}✅ Backend:${NC} http://localhost:8000"
echo -e "   ${GREEN}✅ Frontend:${NC} http://localhost:3000"
echo -e "   ${GREEN}✅ API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}💡 To stop all services, run: ./stop.sh${NC}"
echo -e "${YELLOW}💡 Backend logs: tail -f backend.log${NC}"
echo -e "${YELLOW}💡 Frontend logs: tail -f frontend.log${NC}" 