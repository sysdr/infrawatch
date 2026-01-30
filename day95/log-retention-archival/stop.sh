#!/bin/bash

echo "Stopping Log Retention & Archival System..."

if [ "$1" == "--docker" ]; then
    docker-compose down
else
    pkill -f "python api/main.py"
    pkill -f "npm start"
fi

echo "Stopped!"
