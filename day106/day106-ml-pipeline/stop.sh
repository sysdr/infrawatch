#!/bin/bash
# Day 106 ML Pipeline - Stop script
echo "Stopping Day 106 ML Pipeline..."

pkill -f "uvicorn app.main:app" 2>/dev/null && echo "Backend stopped" || true
pkill -f "vite --port 3106" 2>/dev/null && echo "Frontend stopped" || true
pkill -f "npm run dev" 2>/dev/null || true

echo "All services stopped."
