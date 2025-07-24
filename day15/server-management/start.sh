#!/bin/bash

# Server Management Demo - Start Script
# This script builds, runs, tests, and verifies the demo behavior

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to run tests
run_tests() {
    print_status "Running backend tests..."
    
    # Run backend tests inside the Docker container
    docker-compose -f "$SCRIPT_DIR/docker/docker-compose.yml" exec -T backend python -m pytest tests/ -v
    
    print_success "Backend tests completed"
}

# Function to verify demo behavior
verify_demo() {
    print_status "Verifying demo behavior..."
    
    # Test API endpoints
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Health endpoint working"
    else
        print_error "Health endpoint failed"
        return 1
    fi
    
    # Test root endpoint
    if curl -s http://localhost:8000/ | grep -q "Server Management API"; then
        print_success "Root endpoint working"
    else
        print_error "Root endpoint failed"
        return 1
    fi
    
    # Test servers endpoint
    if curl -s http://localhost:8000/api/servers/ | grep -q "\[\]"; then
        print_success "Servers endpoint working (empty list as expected)"
    else
        print_warning "Servers endpoint returned unexpected data"
    fi
    
    # Test frontend
    print_status "Testing frontend..."
    if curl -s http://localhost:3000/ | grep -q "html"; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend may not be fully loaded yet"
    fi
    
    print_success "Demo verification completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "Server Management Demo - Start Script"
    echo "=========================================="
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    
    # Stop any existing containers
    print_status "Stopping any existing containers..."
    docker-compose -f "$SCRIPT_DIR/docker/docker-compose.yml" down --remove-orphans 2>/dev/null || true
    
    # Build and start services
    print_status "Building and starting services..."
    docker-compose -f "$SCRIPT_DIR/docker/docker-compose.yml" up --build -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Wait for backend
    if ! wait_for_service "http://localhost:8000/health" "Backend API"; then
        print_error "Backend failed to start properly"
        docker-compose -f "$SCRIPT_DIR/docker/docker-compose.yml" logs backend
        exit 1
    fi
    
    # Wait for frontend
    if ! wait_for_service "http://localhost:3000" "Frontend"; then
        print_warning "Frontend may still be starting up"
    fi
    
    # Run tests
    run_tests
    
    # Verify demo behavior
    verify_demo
    
    echo ""
    echo "=========================================="
    print_success "Demo started successfully!"
    echo "=========================================="
    echo ""
    echo "Services:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Frontend:    http://localhost:3000"
    echo "  - Database:    localhost:5432"
    echo ""
    echo "API Documentation:"
    echo "  - Swagger UI:  http://localhost:8000/docs"
    echo "  - ReDoc:       http://localhost:8000/redoc"
    echo ""
    echo "To stop the demo, run: $(dirname "$SCRIPT_DIR")/stop.sh"
    echo "To view logs, run: docker-compose -f $SCRIPT_DIR/docker/docker-compose.yml logs -f"
    echo ""
}

# Run main function
main "$@" 