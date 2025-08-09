#!/bin/bash
set +e

echo "🛑 Stopping Day 20: Server Management UI"

# Kill backend processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "python -m uvicorn app.main:app" 2>/dev/null || true

# Kill frontend processes  
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

echo "✅ All services stopped"
