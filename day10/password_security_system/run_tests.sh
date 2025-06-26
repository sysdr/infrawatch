#!/bin/bash
echo "🧪 Running Password Security Tests"
echo "=================================="

# Install test dependencies
pip install pytest pytest-asyncio httpx fakeredis

# Run tests with verbose output
pytest tests/ -v --asyncio-mode=auto

echo "✅ Tests completed!"
