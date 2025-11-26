#!/bin/bash

echo "🛑 Stopping Real-time Integration System..."

# Stop backend
pkill -f "uvicorn app.main:app"

# Stop frontend
pkill -f "react-scripts start"

# Stop Docker if running
docker-compose down 2>/dev/null

echo "✅ System stopped"
