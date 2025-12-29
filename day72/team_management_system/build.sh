#!/bin/bash

# Team Management System Build Script
# This script builds the project without Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "=== Team Management System Build ==="

# Validate paths
if [ ! -d "$BACKEND_DIR" ]; then
    echo "ERROR: Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "ERROR: Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Setup backend
echo "Setting up backend..."
cd "$BACKEND_DIR"

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found in $BACKEND_DIR"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment activation script not found"
    exit 1
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "Backend setup complete"

# Verify the metadata fix is in place
if grep -q 'team_metadata = Column("metadata"' app/models/team.py; then
    echo "✓ Metadata column fix verified"
else
    echo "WARNING: Metadata column fix may be missing"
fi

# Setup frontend
echo "Setting up frontend..."
cd "$FRONTEND_DIR"

if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found in $FRONTEND_DIR"
    exit 1
fi

npm install
npm run build

echo "Frontend build complete"

echo -e "\n=== Build Complete ==="
echo "To start the system, run: ./startup.sh"
echo "=========================================="
