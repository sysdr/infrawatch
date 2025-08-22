#!/bin/bash

echo "=== Stopping Metrics Collection Engine ==="

# Kill processes if PID files exist
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
fi

if [ -f agent1.pid ]; then
    kill $(cat agent1.pid) 2>/dev/null
    rm agent1.pid
fi

if [ -f agent2.pid ]; then
    kill $(cat agent2.pid) 2>/dev/null
    rm agent2.pid
fi

# Kill any remaining processes
pkill -f "python.*main.py"
pkill -f "npm start"
pkill -f "system_agent.py"
pkill -f "custom_agent.py"

echo "All services stopped"
