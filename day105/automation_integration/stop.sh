#!/bin/bash

echo "Stopping Automation Integration System..."

# Kill backend
pkill -f "uvicorn app.main:app"

# Kill frontend
pkill -f "react-scripts start"

echo "System stopped"
