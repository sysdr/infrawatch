#!/bin/bash
# Quick backend startup script
cd "$(dirname "$0")/backend"
source venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
