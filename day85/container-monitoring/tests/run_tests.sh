#!/bin/bash

# Test runner script for Container Monitoring System

set -e

echo "============================================"
echo "Container Monitoring System - Test Suite"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: Please run this script from the container-monitoring directory${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "backend/venv" ]; then
    echo "Activating virtual environment..."
    source backend/venv/bin/activate
fi

# Install test dependencies if needed
echo "Checking test dependencies..."
cd backend
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install pytest pytest-asyncio httpx > /dev/null 2>&1
fi

echo ""
echo -e "${YELLOW}Running Backend Tests...${NC}"
echo "============================================"

# Run backend tests
pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend tests passed!${NC}"
else
    echo -e "${RED}✗ Backend tests failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}============================================"
echo "All tests completed successfully!"
echo "============================================${NC}"
echo ""
echo "To start the application:"
echo "  1. Backend: cd backend && source venv/bin/activate && uvicorn backend.app.main:app --reload"
echo "  2. Frontend: cd frontend && npm run dev"
echo ""
echo "Dashboard will be available at: http://localhost:3000"
echo "API docs at: http://localhost:8000/docs"
