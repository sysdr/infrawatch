#!/bin/bash

echo "Stopping Export UI System..."

# Kill processes
pkill -f "uvicorn app.main"
pkill -f "react-scripts start"

# Stop Docker containers if running
docker stop export-postgres export-redis 2>/dev/null
docker rm export-postgres export-redis 2>/dev/null

echo "System stopped"
