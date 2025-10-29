#!/bin/bash
echo "🛑 Stopping Notification Delivery System..."
pkill -f "uvicorn"
pkill -f "npm start"
echo "✅ System stopped successfully!"
