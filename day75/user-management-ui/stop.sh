#!/bin/bash

echo "Stopping all services..."
pkill -f "python app/main.py" || true
pkill -f "vite" || true
docker-compose down || true

echo "All services stopped"
