#!/bin/bash
echo "🧹 Cleaning up Password Security System"
echo "======================================"

# Stop Redis if running
echo "Stopping Redis server..."
if pgrep -f redis-server > /dev/null; then
    redis-cli shutdown
    echo "✅ Redis stopped"
else
    echo "ℹ️  Redis was not running"
fi

# Kill any running uvicorn processes
echo "Stopping FastAPI server..."
if pgrep -f uvicorn > /dev/null; then
    pkill -f uvicorn
    echo "✅ FastAPI server stopped"
else
    echo "ℹ️  FastAPI server was not running"
fi

# Kill any Python processes related to our app
echo "Stopping Python processes..."
if pgrep -f "app.main:app" > /dev/null; then
    pkill -f "app.main:app"
    echo "✅ Python app processes stopped"
else
    echo "ℹ️  No Python app processes found"
fi

# Clean up any temporary files
echo "Cleaning up temporary files..."
rm -f *.pyc
rm -rf __pycache__
rm -rf app/__pycache__
rm -rf app/*/__pycache__
rm -rf tests/__pycache__

# Clean up Redis dump files (optional - uncomment if needed)
# echo "Cleaning up Redis dump files..."
# rm -f dump.rdb

echo "✅ Cleanup completed!"
echo "You can now run ./run_demo.sh to start fresh" 