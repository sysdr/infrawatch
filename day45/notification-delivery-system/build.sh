#!/bin/bash

echo "🚀 Building Notification Delivery System"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Build completed successfully!"

# Run the system
echo "🚀 Starting Notification Delivery System..."

# Start backend
echo "🔧 Starting backend server..."
cd backend
source ../venv/bin/activate
python -m pytest tests/ -v
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Notification Delivery System..."
pkill -f "uvicorn"
pkill -f "npm start"
echo "✅ System stopped successfully!"
