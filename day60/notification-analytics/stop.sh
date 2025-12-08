#!/bin/bash
echo "Stopping all services..."
pkill -f "uvicorn"
pkill -f "react-scripts"
echo "Services stopped"
