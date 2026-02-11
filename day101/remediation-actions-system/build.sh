#!/bin/bash
set -e
echo "Building Remediation Actions System..."
cd "$(dirname "$0")"
cd backend
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "Backend setup complete"
cd ../frontend
npm install 2>/dev/null || echo "Frontend: npm install failed (run manually if needed)"
echo "Build complete! Run ./run.sh to start"
