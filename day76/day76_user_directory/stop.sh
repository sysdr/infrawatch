#!/bin/bash

echo "Stopping Day 76 services..."

# Stop Docker containers
docker-compose down

# Kill local processes
pkill -f "uvicorn app.main"
pkill -f "react-scripts start"

echo "All services stopped"
