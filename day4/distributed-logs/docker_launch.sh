#!/bin/bash

# Docker Launch Script for Distributed Log Processor
echo "🐳 Setting up Docker environment for Distributed Log Processing..."

cd distributed-logs

# 1. Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# Copy source code
COPY backend/src/ ./src/
COPY backend/tests/ ./tests/

# Set Python path
ENV PYTHONPATH=/app/src

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the web server
CMD ["python", "src/web_main.py"]
EOF

# 2. Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  log-processor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app/src
      - LOG_LEVEL=INFO
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - ./logs:/app/logs
      - ./backend/src:/app/src:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  logs:
EOF

# 3. Copy the web server main file
cp backend/src/main.py backend/src/web_main.py

# 4. Update requirements.txt if needed
if [ ! -f backend/requirements.txt ]; then
    echo "Creating requirements.txt..."
    cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pytest==7.4.3
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.6.0
EOF
fi

echo "✅ Docker configuration created!"
echo ""
echo "🚀 Building and launching with Docker..."

# Build and run
docker-compose up --build -d

echo ""
echo "🎉 Application launched successfully!"
echo "📊 Dashboard: http://localhost:8000"
echo "🔧 API Stats: http://localhost:8000/api/stats"
echo "❤️ Health Check: http://localhost:8000/health"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"