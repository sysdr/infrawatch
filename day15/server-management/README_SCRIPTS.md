# Server Management Demo Scripts

This directory contains scripts to easily build, run, test, and verify the Server Management demo application.

## Quick Start

### 1. Start the Demo
```bash
./start.sh
```

This script will:
- Check prerequisites (Docker, Docker Compose)
- Stop any existing containers
- Build and start all services (PostgreSQL, Backend API, Frontend)
- Wait for services to be ready
- Run backend tests
- Verify demo behavior
- Display service URLs and documentation links

### 2. Stop the Demo
```bash
./stop.sh
```

This script will:
- Stop all running services
- Provide interactive cleanup options
- Clean up containers, images, and volumes (optional)
- Remove demo data (optional)

### 3. Verify Demo Behavior
```bash
./verify_demo.sh
```

This script will:
- Check if all services are running
- Test API endpoints
- Verify server operations (create, read, list)
- Test frontend accessibility
- Run backend tests
- Provide detailed verification results

## Script Details

### start.sh
**Purpose**: Complete demo startup with verification

**Features**:
- Prerequisites checking
- Automatic service startup
- Health monitoring
- Test execution
- Demo verification
- Colored output for better readability

**Usage**:
```bash
./start.sh
```

### stop.sh
**Purpose**: Clean demo shutdown with cleanup options

**Features**:
- Graceful service shutdown
- Interactive cleanup menu
- Command-line options for automation
- Multiple cleanup levels

**Usage**:
```bash
# Interactive mode (default)
./stop.sh

# Command-line options
./stop.sh --clean        # Stop and clean containers
./stop.sh --full-clean   # Stop and full cleanup
./stop.sh --data-clean   # Stop and remove demo data
./stop.sh --help         # Show help
```

**Cleanup Levels**:
1. **Stop services only** (default)
2. **Stop services + clean containers**
3. **Stop services + clean containers and images**
4. **Stop services + full cleanup** (containers, images, volumes)
5. **Stop services + remove demo data**
6. **Full cleanup** (everything)

### verify_demo.sh
**Purpose**: Comprehensive demo verification

**Features**:
- Service status checking
- API endpoint testing
- Server operations testing
- Frontend verification
- Backend test execution
- Detailed reporting

**Usage**:
```bash
# Full verification (default)
./verify_demo.sh

# Specific verifications
./verify_demo.sh --api-only      # Test only API endpoints
./verify_demo.sh --frontend-only # Test only frontend
./verify_demo.sh --tests-only    # Run only backend tests
./verify_demo.sh --help          # Show help
```

## Services

The demo includes the following services:

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | Database |
| Backend API | 8000 | FastAPI server |
| Frontend | 3000 | React application |

## API Documentation

Once the demo is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **API Root**: http://localhost:8000/

## Troubleshooting

### Common Issues

1. **Port conflicts**: If ports 3000, 8000, or 5432 are in use, stop the conflicting services first.

2. **Docker not running**: Ensure Docker Desktop is running before executing scripts.

3. **Permission denied**: Make sure scripts are executable:
   ```bash
   chmod +x start.sh stop.sh verify_demo.sh
   ```

4. **Services not starting**: Check Docker logs:
   ```bash
   docker-compose -f docker/docker-compose.yml logs -f
   ```

### Manual Verification

If automated verification fails, you can manually check:

1. **Database**: `docker-compose -f docker/docker-compose.yml exec postgres psql -U user -d serverdb`
2. **Backend**: `curl http://localhost:8000/health`
3. **Frontend**: `curl http://localhost:3000/`

### Clean Restart

For a completely clean restart:
```bash
./stop.sh --full-clean
./start.sh
```

## Development

### Adding New Tests

To add new verification tests, edit `verify_demo.sh` and add new test functions.

### Customizing Scripts

The scripts are designed to be easily customizable:
- Modify service URLs in the scripts if needed
- Add new verification steps
- Customize cleanup behavior

### Logs

View real-time logs:
```bash
docker-compose -f docker/docker-compose.yml logs -f
```

View specific service logs:
```bash
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend
docker-compose -f docker/docker-compose.yml logs -f postgres
```

## Requirements

- Docker
- Docker Compose
- curl (for verification)
- jq (for JSON parsing in verification)
- Python 3.x (for running tests)

## Notes

- The scripts use colored output for better readability
- All scripts exit on first error (`set -e`)
- Scripts are designed to be idempotent (safe to run multiple times)
- Interactive prompts are only shown when running in a terminal 