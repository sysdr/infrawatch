#!/bin/bash

echo "Stopping all services..."

# Kill backend
pkill -f "uvicorn app.main:app"

# Kill frontend
pkill -f "vite"

# Stop Redis if we started it
# redis-cli shutdown

echo "All services stopped!"
