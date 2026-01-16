#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Stopping API Security System...${NC}"

# Check for Docker
if [ -f "docker/docker-compose.yml" ]; then
    cd docker
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        echo "Stopping Docker containers..."
        docker-compose down
    fi
    cd ..
fi

# Stop backend
if [ -f "backend.pid" ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

# Stop frontend
if [ -f "frontend.pid" ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

echo -e "${GREEN}✓ Stopped${NC}"
