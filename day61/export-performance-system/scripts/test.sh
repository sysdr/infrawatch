#!/bin/bash

set -e

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running tests..."
echo "Project directory: $PROJECT_DIR"

# Wait for services
echo "Waiting for services to be ready..."
timeout 30 bash -c 'until curl -f http://localhost:8000/ > /dev/null 2>&1; do sleep 1; done' || {
    echo "Error: Backend service is not responding. Please start it first."
    exit 1
}

# Run integration tests
cd "$PROJECT_DIR/tests"
if [ ! -f "test_integration.py" ]; then
    echo "Error: test_integration.py not found"
    exit 1
fi
pytest test_integration.py -v

# Run load test (2 minute test with 100 users)
echo "Running load test..."
if [ ! -f "load_test.py" ]; then
    echo "Error: load_test.py not found"
    exit 1
fi
locust -f load_test.py --headless -u 100 -r 10 -t 2m --host http://localhost:8000 || {
    echo "Warning: Load test may have failed, but continuing..."
}

echo "All tests completed!"
