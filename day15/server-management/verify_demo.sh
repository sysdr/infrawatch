#!/bin/bash

# Server Management Demo - Verification Script
# This script verifies that the demo is working correctly

set -e  # Exit on any error

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

# Function to test API endpoint
test_endpoint() {
    local url=$1
    local expected_pattern=$2
    local description=$3
    
    print_status "Testing $description..."
    
    if curl -s "$url" | grep -q "$expected_pattern"; then
        print_success "$description working"
        return 0
    else
        print_error "$description failed"
        return 1
    fi
}

# Function to test API with JSON response
test_json_endpoint() {
    local url=$1
    local description=$2
    
    print_status "Testing $description..."
    
    response=$(curl -s "$url")
    if echo "$response" | jq . >/dev/null 2>&1; then
        print_success "$description working (valid JSON)"
        return 0
    else
        print_error "$description failed (invalid JSON)"
        return 1
    fi
}

# Function to create test server
create_test_server() {
    print_status "Creating test server..."
    
    # Generate a unique name using timestamp
    timestamp=$(date +%s)
    server_name="demo-server-$timestamp"
    
    response=$(curl -s -X POST "http://localhost:8000/api/servers/" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$server_name\",
            \"hostname\": \"demo.example.com\",
            \"ip_address\": \"192.168.1.100\",
            \"environment\": \"demo\",
            \"region\": \"us-west-2\"
        }")
    
    if echo "$response" | jq . >/dev/null 2>&1; then
        server_id=$(echo "$response" | jq -r '.id')
        print_success "Test server created with ID: $server_id"
        echo "$server_id"
    else
        print_error "Failed to create test server"
        return 1
    fi
}

# Function to test server operations
test_server_operations() {
    print_status "Testing server operations..."
    
    # Create a test server
    server_id=$(create_test_server)
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    # Test getting the server
    if test_json_endpoint "http://localhost:8000/api/servers/$server_id" "Get server by ID"; then
        print_success "Server retrieval working"
    else
        print_error "Server retrieval failed"
        return 1
    fi
    
    # Test listing servers
    if test_json_endpoint "http://localhost:8000/api/servers/" "List servers"; then
        print_success "Server listing working"
    else
        print_error "Server listing failed"
        return 1
    fi
    
    # Test creating a tag
    tag_response=$(curl -s -X POST "http://localhost:8000/api/servers/tags/" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "demo-tag",
            "description": "Demo tag for testing",
            "category": "demo",
            "color": "#3B82F6"
        }')
    
    if echo "$tag_response" | jq . >/dev/null 2>&1; then
        print_success "Tag creation working"
    else
        print_warning "Tag creation failed (may not be implemented)"
    fi
}

# Function to check service status
check_service_status() {
    print_status "Checking service status..."
    
    # Check if containers are running
    if docker-compose -f docker/docker-compose.yml ps --services --filter "status=running" | grep -q .; then
        print_success "Docker services are running"
    else
        print_error "Docker services are not running"
        return 1
    fi
    
    # Check specific services
    services=("postgres" "backend" "frontend")
    for service in "${services[@]}"; do
        if docker-compose -f docker/docker-compose.yml ps "$service" | grep -q "Up"; then
            print_success "$service is running"
        else
            print_error "$service is not running"
            return 1
        fi
    done
}

# Function to test frontend
test_frontend() {
    print_status "Testing frontend..."
    
    # Test if frontend is accessible
    if curl -s http://localhost:3000/ | grep -q "html"; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend may not be fully loaded"
    fi
    
    # Test if frontend can load resources
    if curl -s http://localhost:3000/ | grep -q "script\|link"; then
        print_success "Frontend resources loading"
    else
        print_warning "Frontend resources may not be loading properly"
    fi
}

# Function to run backend tests
run_backend_tests() {
    print_status "Running backend tests..."
    
    cd backend
    if command -v python3 >/dev/null 2>&1; then
        if python3 -m pytest tests/ -v; then
            print_success "Backend tests passed"
        else
            print_error "Backend tests failed"
            cd ..
            return 1
        fi
    else
        if python -m pytest tests/ -v; then
            print_success "Backend tests passed"
        else
            print_error "Backend tests failed"
            cd ..
            return 1
        fi
    fi
    cd ..
}

# Main verification function
main() {
    echo "=========================================="
    echo "Server Management Demo - Verification"
    echo "=========================================="
    
    local failed_tests=0
    
    # Check service status
    if ! check_service_status; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test basic API endpoints
    if ! test_endpoint "http://localhost:8000/health" "healthy" "Health endpoint"; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if ! test_endpoint "http://localhost:8000/" "Server Management API" "Root endpoint"; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test JSON endpoints
    if ! test_json_endpoint "http://localhost:8000/api/servers/" "Servers endpoint"; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test server operations
    if ! test_server_operations; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test frontend
    test_frontend
    
    # Run backend tests
    if ! run_backend_tests; then
        failed_tests=$((failed_tests + 1))
    fi
    
    echo ""
    echo "=========================================="
    if [ $failed_tests -eq 0 ]; then
        print_success "All verifications passed! Demo is working correctly."
    else
        print_error "$failed_tests verification(s) failed. Please check the logs above."
    fi
    echo "=========================================="
    echo ""
    
    return $failed_tests
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --api-only     Test only API endpoints"
        echo "  --frontend-only Test only frontend"
        echo "  --tests-only   Run only backend tests"
        echo ""
        echo "Examples:"
        echo "  $0              # Full verification"
        echo "  $0 --api-only   # Test only API"
        echo "  $0 --tests-only # Run only tests"
        exit 0
        ;;
    --api-only)
        echo "=========================================="
        echo "API-Only Verification"
        echo "=========================================="
        test_endpoint "http://localhost:8000/health" "healthy" "Health endpoint"
        test_endpoint "http://localhost:8000/" "Server Management API" "Root endpoint"
        test_json_endpoint "http://localhost:8000/api/servers/" "Servers endpoint"
        test_server_operations
        exit 0
        ;;
    --frontend-only)
        echo "=========================================="
        echo "Frontend-Only Verification"
        echo "=========================================="
        test_frontend
        exit 0
        ;;
    --tests-only)
        echo "=========================================="
        echo "Backend Tests Only"
        echo "=========================================="
        run_backend_tests
        exit $?
        ;;
esac

# Run main verification
main "$@" 