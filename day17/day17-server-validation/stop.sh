#!/bin/bash

echo "🛑 Stopping Day 17: Server Validation & Health System"

# Function to kill process and verify it's stopped
kill_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "🛑 Stopping $service_name (PID: $pid)..."
        
        # Try graceful shutdown first
        kill $pid 2>/dev/null
        
        # Wait up to 5 seconds for graceful shutdown
        local count=0
        while ps -p $pid > /dev/null 2>&1 && [ $count -lt 5 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            echo "⚠️  Force killing $service_name..."
            kill -9 $pid 2>/dev/null
            sleep 1
        fi
        
        # Verify process is stopped
        if ps -p $pid > /dev/null 2>&1; then
            echo "❌ Failed to stop $service_name (PID: $pid)"
        else
            echo "✅ $service_name stopped successfully"
        fi
        
        # Remove PID file
        rm -f "$pid_file"
    else
        echo "ℹ️  No PID file found for $service_name"
    fi
}

# Function to kill processes by name
kill_by_name() {
    local process_name=$1
    local service_name=$2
    
    echo "🔍 Looking for $service_name processes..."
    local pids=$(pgrep -f "$process_name" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "🛑 Found $service_name processes: $pids"
        echo "$pids" | xargs kill 2>/dev/null
        
        # Wait and force kill if needed
        sleep 2
        local remaining_pids=$(pgrep -f "$process_name" 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo "⚠️  Force killing remaining $service_name processes..."
            echo "$remaining_pids" | xargs kill -9 2>/dev/null
        fi
        
        echo "✅ $service_name processes stopped"
    else
        echo "ℹ️  No $service_name processes found"
    fi
}

# Function to cleanup files and directories
cleanup_files() {
    local pattern=$1
    local description=$2
    
    echo "🧹 Cleaning up $description..."
    local files_found=0
    
    # Find and remove files/directories
    while IFS= read -r -d '' file; do
        if [ -e "$file" ]; then
            rm -rf "$file" 2>/dev/null
            files_found=$((files_found + 1))
        fi
    done < <(find . -name "$pattern" -type f -o -name "$pattern" -type d 2>/dev/null | head -20)
    
    if [ $files_found -gt 0 ]; then
        echo "✅ Removed $files_found $description"
    else
        echo "ℹ️  No $description found"
    fi
}

# Stop backend and frontend processes
kill_process "backend.pid" "Backend"
kill_process "frontend.pid" "Frontend"

# Kill any remaining processes by name (in case PID files are stale)
kill_by_name "python.*app.main" "Backend Python"
kill_by_name "react-scripts" "Frontend React"

# Stop Docker services
echo "🐳 Stopping Docker services..."
docker-compose down
if [ $? -eq 0 ]; then
    echo "✅ Docker services stopped"
else
    echo "⚠️  Docker services may not have been running"
fi

# Comprehensive cleanup of temporary files, cache files, and logs
echo "🧹 Starting comprehensive cleanup..."

# Clean up PID files
echo "🧹 Cleaning up PID files..."
rm -f backend.pid frontend.pid 2>/dev/null

# Python cleanup
cleanup_files "*.pyc" "Python bytecode files"
cleanup_files "__pycache__" "Python cache directories"
cleanup_files "*.pyo" "Python optimized files"
cleanup_files "*.pyd" "Python compiled files"
cleanup_files ".pytest_cache" "Python test cache"
cleanup_files ".coverage" "Python coverage files"
cleanup_files "htmlcov" "Python coverage HTML"
cleanup_files ".mypy_cache" "Python type checker cache"
cleanup_files ".ruff_cache" "Python linter cache"

# JavaScript/Node.js cleanup
cleanup_files "node_modules" "Node.js dependencies"
cleanup_files "npm-debug.log*" "npm debug logs"
cleanup_files "yarn-debug.log*" "yarn debug logs"
cleanup_files "yarn-error.log*" "yarn error logs"
cleanup_files ".npm" "npm cache"
cleanup_files ".yarn" "yarn cache"
cleanup_files ".yarnrc" "yarn config"
cleanup_files "package-lock.json" "npm lock file"
cleanup_files "yarn.lock" "yarn lock file"
cleanup_files ".next" "Next.js build cache"
cleanup_files ".nuxt" "Nuxt.js build cache"
cleanup_files "dist" "Build distribution files"
cleanup_files "build" "Build output files"
cleanup_files ".cache" "General cache directories"

# React/Webpack cleanup
cleanup_files "*.hot-update.*" "React hot update files"
cleanup_files ".webpack" "Webpack cache"
cleanup_files "webpack-stats.json" "Webpack stats"

# Log files cleanup
cleanup_files "*.log" "Log files"
cleanup_files "logs" "Log directories"
cleanup_files "*.out" "Output files"
cleanup_files "*.err" "Error files"

# Temporary files cleanup
cleanup_files "*.tmp" "Temporary files"
cleanup_files "*.temp" "Temporary files"
cleanup_files ".tmp" "Temporary directories"
cleanup_files ".temp" "Temporary directories"
cleanup_files "*~" "Backup files"
cleanup_files ".#*" "Emacs lock files"
cleanup_files ".DS_Store" "macOS system files"
cleanup_files "Thumbs.db" "Windows thumbnail files"

# IDE/Editor cleanup
cleanup_files ".vscode" "VS Code settings"
cleanup_files ".idea" "IntelliJ IDEA settings"
cleanup_files "*.swp" "Vim swap files"
cleanup_files "*.swo" "Vim swap files"
cleanup_files "*~" "Editor backup files"

# OS-specific cleanup
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS specific cleanup
    cleanup_files ".DS_Store" "macOS system files"
    cleanup_files ".AppleDouble" "macOS resource fork"
    cleanup_files ".LSOverride" "macOS system files"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux specific cleanup
    cleanup_files "*.orig" "Backup files"
    cleanup_files "*.rej" "Reject files"
fi

# Clean up any remaining temporary directories
echo "🧹 Cleaning up any remaining temporary directories..."
find . -type d -name "tmp" -o -name "temp" -o -name "cache" 2>/dev/null | while read -r dir; do
    if [ -d "$dir" ] && [ "$dir" != "./venv" ] && [ "$dir" != "./node_modules" ]; then
        rm -rf "$dir" 2>/dev/null
        echo "✅ Removed temporary directory: $dir"
    fi
done

# Check if any processes are still running
echo "🔍 Verifying all services are stopped..."

# Check for backend processes
backend_pids=$(pgrep -f "python.*app.main" 2>/dev/null)
if [ -n "$backend_pids" ]; then
    echo "⚠️  Backend processes still running: $backend_pids"
    echo "   You may need to manually kill these processes"
else
    echo "✅ No backend processes found"
fi

# Check for frontend processes
frontend_pids=$(pgrep -f "react-scripts" 2>/dev/null)
if [ -n "$frontend_pids" ]; then
    echo "⚠️  Frontend processes still running: $frontend_pids"
    echo "   You may need to manually kill these processes"
else
    echo "✅ No frontend processes found"
fi

# Check for Docker containers
docker_containers=$(docker ps --filter "name=day17" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null)
if [ -n "$docker_containers" ]; then
    echo "⚠️  Docker containers still running:"
    echo "$docker_containers"
else
    echo "✅ No Docker containers found"
fi

rm -rf venv
rm -rf backend/venv 


rm -rf node_modules
rm -rf backend/node_modules
rm -rf frontend/node_modules

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "📋 Summary:"
echo "   • Backend processes: Stopped"
echo "   • Frontend processes: Stopped"
echo "   • Docker services: Stopped"
echo "   • PID files: Cleaned up"
echo "   • Python cache files: Cleaned up"
echo "   • JavaScript cache files: Cleaned up"
echo "   • Log files: Cleaned up"
echo "   • Temporary files: Cleaned up"
echo "   • IDE/Editor files: Cleaned up"
echo ""
echo "💡 If you see any remaining processes above, you may need to:"
echo "   • Manually kill them: kill -9 <PID>"
echo "   • Restart your terminal"
echo "   • Check for orphaned processes: ps aux | grep -E '(python|node)'"
echo ""
echo "💡 To start fresh, run: ./start.sh"
