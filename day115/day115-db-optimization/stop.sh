#!/usr/bin/env bash
echo "Stopping Day 115 services..."
# Stop app servers only; leave PostgreSQL running unless you run docker compose down
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
# Ensure nothing is left on API/frontend ports
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
echo "All services stopped."
echo "To stop PostgreSQL too: docker compose down"
