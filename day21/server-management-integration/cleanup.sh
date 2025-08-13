#!/bin/bash

echo "🧹 Cleaning up Server Management Integration System for check-in"
echo "================================================================"

# Remove temporary files
echo "🗑️  Removing temporary files..."
rm -f *.log *.pid

# Backend cleanup
echo "🐍 Cleaning backend..."
cd backend

# Remove virtual environment
if [ -d "venv" ]; then
    echo "   Removing virtual environment..."
    rm -rf venv
fi

# Remove Python cache files
echo "   Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true

# Remove pytest cache
if [ -d ".pytest_cache" ]; then
    echo "   Removing pytest cache..."
    rm -rf .pytest_cache
fi

# Remove coverage files
find . -name ".coverage" -delete 2>/dev/null || true
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true

cd ..

# Frontend cleanup
echo "⚛️  Cleaning frontend..."
cd frontend

# Remove node_modules
if [ -d "node_modules" ]; then
    echo "   Removing node_modules..."
    rm -rf node_modules
fi

# Remove build directory
if [ -d "build" ]; then
    echo "   Removing build directory..."
    rm -rf build
fi

# Remove package-lock.json (will be regenerated)
if [ -f "package-lock.json" ]; then
    echo "   Removing package-lock.json..."
    rm -f package-lock.json
fi

# Remove npm cache
echo "   Cleaning npm cache..."
npm cache clean --force 2>/dev/null || true

cd ..

# Docker cleanup
echo "🐳 Cleaning Docker artifacts..."
if [ -f "docker-compose.yml" ]; then
    echo "   Stopping and removing containers..."
    docker-compose down --volumes --remove-orphans 2>/dev/null || true
fi

# Remove any Docker images created during development
echo "   Removing development Docker images..."
docker image prune -f 2>/dev/null || true

# Remove any dangling images
docker image prune -f --filter "dangling=true" 2>/dev/null || true

# General cleanup
echo "🧽 General cleanup..."

# Remove any temporary files
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remove any backup files
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.backup" -delete 2>/dev/null || true

# Remove any swap files
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

echo ""
echo "✅ Cleanup complete! The project is ready for check-in."
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git status"
echo "   2. Add files: git add ."
echo "   3. Commit: git commit -m 'Your commit message'"
echo "   4. Push: git push"
