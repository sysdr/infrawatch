#!/bin/bash

echo "🔍 Starting Error Monitoring Dashboard..."
echo "========================================"

# Function to monitor backend errors
monitor_backend() {
    echo "📊 Backend Error Monitor (PID: $(ps aux | grep 'uvicorn app.main:app' | grep -v grep | awk '{print $2}'))"
    echo "----------------------------------------"
    
    # Monitor backend process and look for errors
    while true; do
        # Check if backend is still running
        if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
            echo "❌ Backend process died!"
            break
        fi
        
        # Test backend health
        response=$(curl -s -w "%{http_code}" http://localhost:8000/ 2>/dev/null)
        http_code="${response: -3}"
        if [ "$http_code" != "200" ] && [ "$http_code" != "404" ]; then
            echo "⚠️  Backend HTTP Error: $http_code"
        fi
        
        sleep 5
    done
}

# Function to monitor frontend errors
monitor_frontend() {
    echo "🌐 Frontend Error Monitor (PID: $(ps aux | grep 'react-scripts start' | grep -v grep | awk '{print $2}'))"
    echo "----------------------------------------"
    
    while true; do
        # Check if frontend is still running
        if ! pgrep -f "react-scripts start" > /dev/null; then
            echo "❌ Frontend process died!"
            break
        fi
        
        # Test frontend health
        response=$(curl -s -w "%{http_code}" http://localhost:3000 2>/dev/null)
        http_code="${response: -3}"
        if [ "$http_code" != "200" ]; then
            echo "⚠️  Frontend HTTP Error: $http_code"
        fi
        
        sleep 5
    done
}

# Function to monitor Redis
monitor_redis() {
    echo "🗄️  Redis Monitor (PID: $(ps aux | grep 'redis-server' | grep -v grep | awk '{print $2}'))"
    echo "----------------------------------------"
    
    while true; do
        # Check if Redis is still running
        if ! pgrep -f "redis-server" > /dev/null; then
            echo "❌ Redis process died!"
            break
        fi
        
        # Test Redis connection
        if ! redis-cli ping > /dev/null 2>&1; then
            echo "⚠️  Redis connection failed!"
        fi
        
        sleep 5
    done
}

# Function to check for common error patterns
check_error_patterns() {
    echo "🔍 Error Pattern Checker"
    echo "----------------------------------------"
    
    while true; do
        # Check for common error files
        if [ -f "backend.log" ] && grep -q "ERROR\|Exception\|Traceback" backend.log 2>/dev/null; then
            echo "❌ Backend errors detected in backend.log"
            grep -i "error\|exception\|traceback" backend.log | tail -3
        fi
        
        if [ -f "frontend.log" ] && grep -q "ERROR\|Failed\|Error" frontend.log 2>/dev/null; then
            echo "❌ Frontend errors detected in frontend.log"
            grep -i "error\|failed" frontend.log | tail -3
        fi
        
        # Check for high memory usage
        backend_mem=$(ps aux | grep "uvicorn app.main:app" | grep -v grep | awk '{print $6}' | head -1)
        frontend_mem=$(ps aux | grep "react-scripts start" | grep -v grep | awk '{print $6}' | head -1)
        
        if [ ! -z "$backend_mem" ] && [ "$backend_mem" -gt 100000 ]; then
            echo "⚠️  High backend memory usage: ${backend_mem}KB"
        fi
        
        if [ ! -z "$frontend_mem" ] && [ "$frontend_mem" -gt 200000 ]; then
            echo "⚠️  High frontend memory usage: ${frontend_mem}KB"
        fi
        
        sleep 10
    done
}

# Start all monitoring functions in background
monitor_backend &
monitor_frontend &
monitor_redis &
check_error_patterns &

# Wait for any background process to finish
wait 