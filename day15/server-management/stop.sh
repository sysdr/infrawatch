#!/bin/bash

# Server Management Demo - Stop Script
# This script stops and cleans up the demo environment

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if containers are running
containers_running() {
    docker-compose -f "$SCRIPT_DIR/docker/docker-compose.yml" ps --services --filter "status=running" | grep -q .
}

# Function to stop services
stop_services() {
    print_status "Stopping Docker services..."
    
    if containers_running; then
        docker-compose -f "$SCRIPT_DIR/docker/docker-compose.yml" down
        print_success "Services stopped successfully"
    else
        print_warning "No running services found"
    fi
}

# Function to clean up containers and images
cleanup() {
    local cleanup_level=${1:-"containers"}
    
    case $cleanup_level in
        "containers")
            print_status "Cleaning up stopped containers..."
            docker container prune -f >/dev/null 2>&1 || true
            ;;
        "images")
            print_status "Cleaning up unused images..."
            docker image prune -f >/dev/null 2>&1 || true
            ;;
        "volumes")
            print_status "Cleaning up unused volumes..."
            docker volume prune -f >/dev/null 2>&1 || true
            ;;
        "all")
            print_status "Performing full cleanup..."
            docker system prune -f >/dev/null 2>&1 || true
            ;;
    esac
}

# Function to remove demo data
remove_demo_data() {
    print_status "Removing demo data..."
    
    # Remove test database file if it exists
    if [ -f "$SCRIPT_DIR/backend/test.db" ]; then
        rm -f "$SCRIPT_DIR/backend/test.db"
        print_success "Removed test database"
    fi
    
    # Remove any Python cache files
    find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Demo data cleaned up"
}

# Function to show cleanup options
show_cleanup_menu() {
    echo ""
    echo "Cleanup Options:"
    echo "  1) Stop services only (default)"
    echo "  2) Stop services + clean containers"
    echo "  3) Stop services + clean containers and images"
    echo "  4) Stop services + full cleanup (containers, images, volumes)"
    echo "  5) Stop services + remove demo data"
    echo "  6) Full cleanup (everything)"
    echo ""
    read -p "Choose cleanup level (1-6) [default: 1]: " choice
    
    case $choice in
        2)
            cleanup "containers"
            ;;
        3)
            cleanup "containers"
            cleanup "images"
            ;;
        4)
            cleanup "all"
            ;;
        5)
            remove_demo_data
            ;;
        6)
            cleanup "all"
            remove_demo_data
            ;;
        *)
            print_status "Performing minimal cleanup (stop services only)"
            ;;
    esac
}

# Main execution
main() {
    echo "=========================================="
    echo "Server Management Demo - Stop Script"
    echo "=========================================="
    
    # Check if Docker Compose file exists
    if [ ! -f "$SCRIPT_DIR/docker/docker-compose.yml" ]; then
        print_error "Docker Compose file not found at $SCRIPT_DIR/docker/docker-compose.yml"
        exit 1
    fi
    
    # Stop services
    stop_services
    
    # Show cleanup options if interactive
    if [ -t 0 ]; then
        show_cleanup_menu
    else
        # Non-interactive mode - just clean containers
        cleanup "containers"
    fi
    
    echo ""
    echo "=========================================="
    print_success "Demo stopped successfully!"
    echo "=========================================="
    echo ""
    echo "To start the demo again, run: $SCRIPT_DIR/start.sh"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean        Stop services and clean containers"
        echo "  --full-clean   Stop services and perform full cleanup"
        echo "  --data-clean   Stop services and remove demo data"
        echo ""
        echo "Examples:"
        echo "  $0              # Interactive cleanup"
        echo "  $0 --clean      # Stop and clean containers"
        echo "  $0 --full-clean # Stop and full cleanup"
        exit 0
        ;;
    --clean)
        stop_services
        cleanup "containers"
        print_success "Demo stopped and containers cleaned"
        exit 0
        ;;
    --full-clean)
        stop_services
        cleanup "all"
        remove_demo_data
        print_success "Demo stopped and full cleanup completed"
        exit 0
        ;;
    --data-clean)
        stop_services
        remove_demo_data
        print_success "Demo stopped and demo data removed"
        exit 0
        ;;
esac

# Run main function
main "$@" 