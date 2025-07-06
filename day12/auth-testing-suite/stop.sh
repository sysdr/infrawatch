#!/bin/bash

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

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed."
        exit 1
    fi
}

# Stop all services
stop_services() {
    print_status "Stopping all services..."
    
    if docker-compose down --remove-orphans; then
        print_success "All services stopped successfully"
    else
        print_error "Failed to stop some services"
        exit 1
    fi
}

# Clean up Docker resources (optional)
cleanup_resources() {
    local choice
    echo ""
    print_status "Do you want to clean up Docker resources? (y/N)"
    read -r choice
    
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up Docker resources..."
        
        # Remove unused containers
        if docker container prune -f > /dev/null 2>&1; then
            print_success "Removed unused containers"
        fi
        
        # Remove unused networks
        if docker network prune -f > /dev/null 2>&1; then
            print_success "Removed unused networks"
        fi
        
        # Remove unused images (optional)
        print_status "Do you want to remove unused images as well? (y/N)"
        read -r choice
        if [[ "$choice" =~ ^[Yy]$ ]]; then
            if docker image prune -f > /dev/null 2>&1; then
                print_success "Removed unused images"
            fi
        fi
        
        print_success "Cleanup completed"
    else
        print_status "Skipping cleanup"
    fi
}

# Show final status
show_status() {
    print_status "Current Docker containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(auth-testing|postgres|redis)" || echo "No auth-testing containers found"
    
    echo ""
    print_status "To start services again: ./demo.sh"
}

# Main execution
main() {
    print_status "Stopping Auth Testing Suite Demo..."
    echo ""
    
    # Pre-flight checks
    check_docker_compose
    
    # Stop services
    stop_services
    
    # Optional cleanup
    cleanup_resources
    
    # Show final status
    show_status
    
    print_success "Demo environment stopped!"
}

# Run main function
main "$@" 