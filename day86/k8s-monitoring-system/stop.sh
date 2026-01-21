#!/bin/bash

echo "Stopping all services..."
docker-compose down
pkill -f "uvicorn app.main:app"
pkill -f "react-scripts start"
echo "All services stopped."
