#!/bin/bash
# Run backend without killing port 8000. Use if start_backend.sh fails or port is in use.
# Start backend on port 8000 (or 8001 if 8000 is in use).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"
export PYTHONPATH="$SCRIPT_DIR/backend:$PYTHONPATH"

if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
    ./venv/bin/pip install -q -r requirements.txt
fi

"$SCRIPT_DIR/backend/venv/bin/python" -c "from app.models.database import init_db; init_db()" 2>/dev/null || true

echo "Starting backend at http://localhost:8000 (Ctrl+C to stop)"
exec "$SCRIPT_DIR/backend/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000
