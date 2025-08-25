#!/bin/bash

echo "🧹 Cleaning up project for check-in..."

# Remove virtual environment
if [ -d "venv" ]; then
    echo "🗑️  Removing Python virtual environment..."
    rm -rf venv
fi

# Remove Python cache files
echo "🗑️  Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Remove pytest cache
if [ -d ".pytest_cache" ]; then
    echo "🗑️  Removing pytest cache..."
    rm -rf .pytest_cache
fi

# Remove Node.js dependencies
if [ -d "frontend/node_modules" ]; then
    echo "🗑️  Removing Node.js dependencies..."
    rm -rf frontend/node_modules
fi

# Remove package-lock.json (will be regenerated)
if [ -f "frontend/package-lock.json" ]; then
    echo "🗑️  Removing package-lock.json..."
    rm -f frontend/package-lock.json
fi

# Remove environment file
if [ -f ".env" ]; then
    echo "🗑️  Removing environment file..."
    rm -f .env
fi

# Remove PID files
echo "🗑️  Removing PID files..."
find . -name "*.pid" -delete 2>/dev/null || true

# Remove any log files
echo "🗑️  Removing log files..."
find . -name "*.log" -delete 2>/dev/null || true

# Remove temporary files
echo "🗑️  Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true

# Remove macOS and Windows system files
echo "🗑️  Removing system files..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

echo "✅ Cleanup completed successfully!"
echo ""
echo "📋 Ready for check-in! The following items have been removed:"
echo "   • Python virtual environment (venv/)"
echo "   • Python cache files (__pycache__/, *.pyc)"
echo "   • Node.js dependencies (node_modules/)"
echo "   • Environment file (.env)"
echo "   • Pytest cache (.pytest_cache/)"
echo "   • PID files (*.pid)"
echo "   • Log files (*.log)"
echo "   • Temporary files (*.tmp)"
echo "   • System files (.DS_Store, Thumbs.db)"
echo ""
echo "💡 To restore the development environment, run: ./start.sh"
