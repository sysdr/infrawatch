#!/bin/bash

echo "🛑 Stopping Task Scheduling System..."

# Stop all services
docker-compose down

# Remove unused containers and networks
docker-compose down --remove-orphans

echo "✅ Services stopped"
