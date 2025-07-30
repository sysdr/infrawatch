#!/bin/bash

# Day 16: Server CRUD Operations - Stop Script
# This script stops all running services

set -e

echo "🛑 Stopping Day 16: Server CRUD Operations"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to kill process by port
kill_by_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        print_status "Stopping $service_name on port $port (PID: $pid)..."
        kill -TERM $pid 2>/dev/null || true
        sleep 2
        if kill -0 $pid 2>/dev/null; then
            print_warning "Force killing $service_name..."
            kill -KILL $pid 2>/dev/null || true
        fi
        print_success "$service_name stopped"
    else
        print_status "$service_name not running on port $port"
    fi
}

# Function to kill process by name
kill_by_name() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        print_status "Stopping $process_name processes..."
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        echo "$pids" | xargs kill -KILL 2>/dev/null || true
        print_success "$process_name processes stopped"
    else
        print_status "No $process_name processes found"
    fi
}

# Stop frontend (React development server)
kill_by_port 3000 "Frontend (React)"

# Stop backend (FastAPI server)
kill_by_port 8000 "Backend (FastAPI)"

# Stop Redis
kill_by_name "redis-server"

# Stop any remaining Node.js processes from the project
print_status "Cleaning up Node.js processes..."
pkill -f "node.*start" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true

# Stop any remaining Python processes from the project
print_status "Cleaning up Python processes..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -f "python.*demo_data.py" 2>/dev/null || true

# Check if any processes are still running
echo ""
print_status "Checking for remaining processes..."

FRONTEND_RUNNING=$(lsof -ti:3000 2>/dev/null | wc -l)
BACKEND_RUNNING=$(lsof -ti:8000 2>/dev/null | wc -l)
REDIS_RUNNING=$(pgrep redis-server 2>/dev/null | wc -l)

if [ $FRONTEND_RUNNING -eq 0 ] && [ $BACKEND_RUNNING -eq 0 ] && [ $REDIS_RUNNING -eq 0 ]; then
    print_success "All services stopped successfully!"
else
    print_warning "Some services may still be running:"
    [ $FRONTEND_RUNNING -gt 0 ] && echo "   Frontend: Still running on port 3000"
    [ $BACKEND_RUNNING -gt 0 ] && echo "   Backend: Still running on port 8000"
    [ $REDIS_RUNNING -gt 0 ] && echo "   Redis: Still running"
fi

echo ""
print_success "Stop script completed!"
echo "🚀 To restart, run: ./start.sh"
