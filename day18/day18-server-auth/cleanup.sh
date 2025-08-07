#!/bin/bash

echo "🧹 Starting Project Cleanup"
echo "=========================="

# Stop any running services first
echo "🛑 Stopping running services..."
./stop.sh 2>/dev/null || true

# Remove log files
echo "🗑️  Removing log files..."
rm -f *.log
rm -f backend.log
rm -f frontend.log

# Remove PID files
echo "🗑️  Removing PID files..."
rm -f .backend.pid
rm -f .frontend.pid
rm -f frontend/.backend.pid
rm -f frontend/.frontend.pid

# Remove Python cache files
echo "🗑️  Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove .DS_Store files (macOS)
echo "🗑️  Removing .DS_Store files..."
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remove node_modules
echo "🗑️  Removing node_modules..."
rm -rf frontend/node_modules 2>/dev/null || true

# Remove virtual environment
echo "🗑️  Removing virtual environment..."
rm -rf backend/venv 2>/dev/null || true

# Remove temporary files
echo "🗑️  Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true

# Remove backup files
echo "🗑️  Removing backup files..."
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.backup" -delete 2>/dev/null || true

# Remove empty directories
echo "🗑️  Removing empty directories..."
find . -type d -empty -delete 2>/dev/null || true

# Remove IDE files
echo "🗑️  Removing IDE files..."
rm -rf .vscode 2>/dev/null || true
rm -rf .idea 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

# Remove test artifacts
echo "🗑️  Removing test artifacts..."
rm -rf .pytest_cache 2>/dev/null || true
rm -rf htmlcov 2>/dev/null || true
rm -rf coverage 2>/dev/null || true
rm -f .coverage 2>/dev/null || true

# Remove build artifacts
echo "🗑️  Removing build artifacts..."
rm -rf build 2>/dev/null || true
rm -rf dist 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove npm/yarn artifacts
echo "🗑️  Removing npm/yarn artifacts..."
rm -f npm-debug.log 2>/dev/null || true
rm -f yarn-debug.log 2>/dev/null || true
rm -rf .npm 2>/dev/null || true
rm -rf .yarn 2>/dev/null || true

# Clean environment files (but keep .env.example)
echo "🧹 Cleaning environment files..."
find . -name ".env" ! -name ".env.example" -delete 2>/dev/null || true

# Remove lock files (optional - uncomment if you want to remove them)
# echo "🗑️  Removing lock files..."
# rm -f package-lock.json 2>/dev/null || true
# rm -f yarn.lock 2>/dev/null || true

echo ""
echo "✅ Cleanup completed successfully!"
echo "================================"
echo "📊 Cleanup Summary:"
echo "  • Removed log files"
echo "  • Removed PID files"
echo "  • Removed Python cache files"
echo "  • Removed node_modules"
echo "  • Removed virtual environment"
echo "  • Removed temporary files"
echo "  • Removed IDE files"
echo "  • Removed test artifacts"
echo "  • Removed build artifacts"
echo ""
echo "🚀 To restart the system:"
echo "  ./start.sh"
echo ""
echo "💡 Note: The system will recreate necessary files when restarted." 