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

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
}

# Stop any existing containers
stop_existing() {
    print_status "Stopping any existing containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
}

# Build and start all services
build_and_start() {
    print_status "Building and starting all services..."
    
    # Build images
    print_status "Building Docker images..."
    if ! docker-compose build; then
        print_error "Failed to build Docker images"
        exit 1
    fi
    
    # Start services
    print_status "Starting services..."
    if ! docker-compose up -d; then
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    timeout=60
    while ! docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "PostgreSQL failed to start within 60 seconds"
            exit 1
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout=30
    while ! docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "Redis failed to start within 30 seconds"
            exit 1
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    print_success "Redis is ready"
    
    # Wait for Backend
    print_status "Waiting for Backend API..."
    timeout=60
    while ! curl -f http://localhost:8000/api/health > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "Backend API failed to start within 60 seconds"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    print_success "Backend API is ready"
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    timeout=60
    while ! curl -f http://localhost:3000 > /dev/null 2>&1; do
        if [ $timeout -le 0 ]; then
            print_error "Frontend failed to start within 60 seconds"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    print_success "Frontend is ready"
}

# Show service status
show_status() {
    print_status "Service Status:"
    echo ""
    docker-compose ps
    echo ""
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Health Check: http://localhost:8000/api/health"
    echo "  PostgreSQL: localhost:5432"
    echo "  Redis: localhost:6379"
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop services: ./stop.sh"
}

# Main execution
main() {
    print_status "Starting Auth Testing Suite Demo..."
    echo ""
    
    # Pre-flight checks
    check_docker
    check_docker_compose
    
    # Stop existing containers
    stop_existing
    
    # Build and start services
    build_and_start
    
    # Wait for services to be ready
    wait_for_services
    
    # Show final status
    show_status
    
    print_success "Demo environment is ready!"
}

# Run main function
main "$@" 