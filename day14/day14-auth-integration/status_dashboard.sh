#!/bin/bash

# Status Dashboard for Auth Integration Services
# Run this script to get a real-time overview of all services

clear
echo "🚀 Auth Integration - Service Status Dashboard"
echo "=============================================="
echo ""

while true; do
    # Get current timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Clear screen and show header
    clear
    echo "🚀 Auth Integration - Service Status Dashboard"
    echo "=============================================="
    echo "Last Updated: $timestamp"
    echo ""
    
    # Backend Status
    echo "📊 BACKEND SERVICE"
    echo "------------------"
    backend_health=$(curl -s http://localhost:8000/api/health 2>/dev/null | jq -r '.status' 2>/dev/null)
    if [ "$backend_health" = "healthy" ]; then
        echo "✅ Status: $backend_health"
        echo "🌐 URL: http://localhost:8000"
        echo "📚 Docs: http://localhost:8000/docs"
    else
        echo "❌ Status: Not responding"
    fi
    
    # Frontend Status
    echo ""
    echo "🌐 FRONTEND SERVICE"
    echo "------------------"
    frontend_code=$(curl -s -w "%{http_code}" http://localhost:3000 2>/dev/null | tail -c 4)
    if [ "$frontend_code" = "200" ]; then
        echo "✅ Status: Running"
        echo "🌐 URL: http://localhost:3000"
    else
        echo "❌ Status: Not responding (HTTP $frontend_code)"
    fi
    
    # Redis Status
    echo ""
    echo "🗄️  REDIS SERVICE"
    echo "----------------"
    redis_ping=$(redis-cli ping 2>/dev/null)
    if [ "$redis_ping" = "PONG" ]; then
        echo "✅ Status: Running"
        echo "🔌 Port: 6379"
    else
        echo "❌ Status: Not responding"
    fi
    
    # Process Information
    echo ""
    echo "🔧 PROCESS INFORMATION"
    echo "---------------------"
    
    # Backend process
    backend_pid=$(ps aux | grep "uvicorn app.main:app" | grep -v grep | awk '{print $2}')
    if [ ! -z "$backend_pid" ]; then
        backend_mem=$(ps -p $backend_pid -o rss= 2>/dev/null | awk '{print $1/1024 " MB"}')
        echo "📊 Backend PID: $backend_pid (Memory: $backend_mem)"
    else
        echo "❌ Backend: Not running"
    fi
    
    # Frontend process
    frontend_pid=$(ps aux | grep "react-scripts start" | grep -v grep | awk '{print $2}')
    if [ ! -z "$frontend_pid" ]; then
        frontend_mem=$(ps -p $frontend_pid -o rss= 2>/dev/null | awk '{print $1/1024 " MB"}')
        echo "🌐 Frontend PID: $frontend_pid (Memory: $frontend_mem)"
    else
        echo "❌ Frontend: Not running"
    fi
    
    # Redis process
    redis_pid=$(ps aux | grep "redis-server" | grep -v grep | awk '{print $2}' | head -1)
    if [ ! -z "$redis_pid" ]; then
        redis_mem=$(ps -p $redis_pid -o rss= 2>/dev/null | awk '{print $1/1024 " MB"}')
        echo "🗄️  Redis PID: $redis_pid (Memory: $redis_mem)"
    else
        echo "❌ Redis: Not running"
    fi
    
    # Error Monitoring
    echo ""
    echo "🔍 ERROR MONITORING"
    echo "-------------------"
    
    # Check for recent errors in logs
    if [ -f "backend.log" ]; then
        recent_backend_errors=$(grep -i "error\|exception\|traceback" backend.log 2>/dev/null | wc -l)
        echo "📊 Backend errors (log): $recent_backend_errors"
    else
        echo "📊 Backend errors (log): No log file found"
    fi
    
    if [ -f "frontend.log" ]; then
        recent_frontend_errors=$(grep -i "error\|failed" frontend.log 2>/dev/null | wc -l)
        echo "🌐 Frontend errors (log): $recent_frontend_errors"
    else
        echo "🌐 Frontend errors (log): No log file found"
    fi
    
    # System Resources
    echo ""
    echo "💻 SYSTEM RESOURCES"
    echo "-------------------"
    cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    memory_usage=$(top -l 1 | grep "PhysMem" | awk '{print $2}' | sed 's/[^0-9]//g')
    echo "🖥️  CPU Usage: ${cpu_usage}%"
    echo "💾 Memory Usage: ${memory_usage}MB"
    
    # Instructions
    echo ""
    echo "💡 COMMANDS"
    echo "-----------"
    echo "🛑 Stop all services: ./stop.sh"
    echo "🚀 Start all services: ./start.sh"
    echo "🔍 Monitor errors: ./monitor_errors.sh"
    echo "📊 View logs: tail -f backend.log frontend.log"
    echo ""
    echo "Press Ctrl+C to exit"
    
    # Wait 5 seconds before updating
    sleep 5
done 