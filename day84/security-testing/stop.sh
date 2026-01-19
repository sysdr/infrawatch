#!/bin/bash

echo "Stopping all services..."
pkill -f uvicorn
pkill -f "npm start"
pkill -f node

echo "Services stopped"
