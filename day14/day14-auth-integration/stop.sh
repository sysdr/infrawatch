#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Auth Integration Services...${NC}"

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}🔄 Stopping $service_name (PID: $pid)...${NC}"
            kill -TERM $pid
            sleep 2
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}🔄 Force killing $service_name...${NC}"
                kill -KILL $pid
            fi
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name was not running${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  PID file for $service_name not found${NC}"
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}🔄 Stopping $service_name on port $port...${NC}"
        lsof -ti:$port | xargs kill -TERM
        sleep 2
        
        # Force kill if still running
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            echo -e "${YELLOW}🔄 Force killing $service_name on port $port...${NC}"
            lsof -ti:$port | xargs kill -KILL
        fi
        echo -e "${GREEN}✅ $service_name stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  $service_name was not running on port $port${NC}"
    fi
}

# Stop services by PID files
echo -e "${BLUE}🔍 Stopping services by PID files...${NC}"
kill_by_pid_file "backend.pid" "Backend"
kill_by_pid_file "frontend.pid" "Frontend"

# Stop services by port (fallback method)
echo -e "${BLUE}🔍 Stopping services by port...${NC}"
kill_port 8000 "Backend"
kill_port 3000 "Frontend"

# Stop Redis
echo -e "${BLUE}📦 Stopping Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${YELLOW}🔄 Stopping Redis...${NC}"
        redis-cli shutdown
        sleep 2
        
        # Force kill if still running
        if lsof -Pi :6379 -sTCP:LISTEN -t >/dev/null ; then
            echo -e "${YELLOW}🔄 Force killing Redis...${NC}"
            lsof -ti:6379 | xargs kill -KILL
        fi
        echo -e "${GREEN}✅ Redis stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis was not running${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis CLI not found, trying to kill by port...${NC}"
    kill_port 6379 "Redis"
fi

# Clean up any remaining processes
echo -e "${BLUE}🧹 Cleaning up remaining processes...${NC}"

# Kill any remaining uvicorn processes
pkill -f "uvicorn" 2>/dev/null && echo -e "${GREEN}✅ Cleaned up uvicorn processes${NC}"

# Kill any remaining npm processes
pkill -f "react-scripts" 2>/dev/null && echo -e "${GREEN}✅ Cleaned up React processes${NC}"

# Kill any remaining node processes (be careful with this)
pkill -f "node.*3000" 2>/dev/null && echo -e "${GREEN}✅ Cleaned up Node.js processes on port 3000${NC}"

# Remove PID files
rm -f backend.pid frontend.pid

echo -e "${GREEN}🎉 All services stopped successfully!${NC}"
echo -e "${BLUE}📊 Final Status:${NC}"

# Check final status
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "   ${GREEN}✅ Backend:${NC} Stopped"
else
    echo -e "   ${RED}❌ Backend:${NC} Still running on port 8000"
fi

if ! lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "   ${GREEN}✅ Frontend:${NC} Stopped"
else
    echo -e "   ${RED}❌ Frontend:${NC} Still running on port 3000"
fi

if ! lsof -Pi :6379 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "   ${GREEN}✅ Redis:${NC} Stopped"
else
    echo -e "   ${RED}❌ Redis:${NC} Still running on port 6379"
fi

echo ""
echo -e "${YELLOW}💡 To start all services again, run: ./start.sh${NC}" 