#!/bin/bash

echo "Stopping Data Protection System..."

if [ -f docker/docker-compose.yml ]; then
    cd docker
    docker-compose down
    cd ..
else
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
    fi
    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
    fi
fi

echo "Services stopped"
