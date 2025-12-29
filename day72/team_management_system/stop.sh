#!/bin/bash

echo "Stopping Team Management System..."

# Kill processes
pkill -f "uvicorn app.main:app"
pkill -f "react-scripts start"

# Docker
docker-compose down

echo "Stopped"
