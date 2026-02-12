#!/bin/bash
# Run demo: seed data and ensure dashboard shows non-zero metrics.
# Use full path so it works from any cwd.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo "Seeding demo data (requires backend and PostgreSQL running)..."
cd backend
PYTHONPATH=. python ../scripts/seed_demo_data.py
cd ..
echo "Done. Open http://localhost:3000 and check Dashboard - Total Workflows, Success Rate, and Recent Executions should be non-zero."
