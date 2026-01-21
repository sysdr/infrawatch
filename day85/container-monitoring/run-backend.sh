#!/bin/bash

# Get the script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"

# Check if backend directory exists
if [ ! -d "${BACKEND_DIR}" ]; then
    echo "Error: Backend directory not found at ${BACKEND_DIR}"
    exit 1
fi

# Change to project root directory
cd "${SCRIPT_DIR}" || exit 1

# Check if venv exists
if [ ! -d "${BACKEND_DIR}/venv" ]; then
    echo "Error: Virtual environment not found. Please run ./build.sh first"
    exit 1
fi

# Activate venv and start server
source "${BACKEND_DIR}/venv/bin/activate"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

python -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
from backend.app.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000)
"
