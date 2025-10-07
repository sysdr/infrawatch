#!/bin/bash

echo "🛑 Stopping Alert Rules API Application..."

# Kill backend processes
pkill -f "python main.py" || true
pkill -f "uvicorn" || true

# Kill frontend processes
pkill -f "npm start" || true
pkill -f "react-scripts" || true

echo "✅ Application stopped successfully!"
