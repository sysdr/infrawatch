#!/bin/bash

echo "🚀 Starting RBAC System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python scripts/init_db.py

# Run the application
echo "🌐 Starting FastAPI server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
