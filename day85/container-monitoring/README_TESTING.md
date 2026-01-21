# Testing Guide - Container Monitoring System

## Test Suite Overview

This project includes comprehensive tests for both backend and frontend components.

## Running Tests

### Quick Test Run

```bash
cd container-monitoring
./tests/run_tests.sh
```

### Individual Test Suites

#### Backend Tests

```bash
cd container-monitoring/backend
source venv/bin/activate
pytest tests/ -v
```

#### Specific Test Files

```bash
# Test Docker service
pytest tests/test_docker_service.py -v

# Test metrics collector
pytest tests/test_metrics_collector.py -v

# Test API routes
pytest tests/test_api_routes.py -v

# Test WebSocket integration
pytest tests/test_websocket_integration.py -v

# Test alert manager
pytest tests/test_alert_manager.py -v
```

## Test Coverage

### Backend Tests

1. **test_docker_service.py**
   - Container listing
   - Container stats retrieval
   - Container health checks

2. **test_metrics_collector.py**
   - Metrics collection
   - Baseline calculation
   - Anomaly detection

3. **test_api_routes.py**
   - REST API endpoints
   - WebSocket connections
   - Health checks
   - Container endpoints

4. **test_websocket_integration.py**
   - WebSocket connection handling
   - Empty state handling
   - Keepalive mechanism
   - Multiple connections

5. **test_alert_manager.py**
   - Alert creation
   - Duplicate prevention
   - Health alerts
   - Restart tracking

### Frontend Tests

Frontend tests are documented in `test_frontend_integration.py` and should be run with React Testing Library in a browser environment.

## Starting the Dashboard

### Quick Start

```bash
cd container-monitoring
./start_dashboard.sh
```

This will start both backend and frontend servers automatically.

### Manual Start

**Terminal 1 - Backend:**
```bash
cd container-monitoring/backend
source venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd container-monitoring/frontend
npm run dev
```

## Accessing the Dashboard

Once both servers are running:

- **Dashboard:** http://localhost:3000 (or check terminal for actual port)
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Test Scenarios

### 1. Empty State Test
- Start dashboard with no Docker containers running
- Should show "No containers running" message
- Connection status should be "Connected"

### 2. Container Monitoring Test
- Start a test container: `docker run -d --name test-container nginx`
- Dashboard should show the container
- Metrics should update in real-time
- CPU and Memory charts should display data

### 3. WebSocket Connection Test
- Open browser DevTools → Network → WS
- Verify WebSocket connections to `/api/v1/ws/metrics` and `/api/v1/ws/events`
- Check that messages are being received

### 4. Alert Test
- Create a container with high resource usage
- Verify alerts appear in the Alerts panel
- Check alert severity colors (warning/critical)

## Troubleshooting

### Tests Fail
- Ensure Docker is running: `docker info`
- Check backend dependencies: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.11+)

### Dashboard Shows Disconnected
- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console for WebSocket errors
- Verify CORS settings in backend

### No Containers Showing
- Check if Docker containers are running: `docker ps`
- Verify Docker socket access: `ls -l /var/run/docker.sock`
- Check backend logs for errors

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
cd backend && pip install -r requirements.txt pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v --tb=short
```

## Test Data

The tests use real Docker containers when available. For testing without Docker:

- Mock Docker service responses
- Use test fixtures for container data
- Simulate WebSocket messages

## Performance Tests

For load testing, use Locust (included in requirements):

```bash
# Create a locustfile.py for API load testing
locust -f locustfile.py --host=http://localhost:8000
```

## Coverage Report

Generate coverage report:

```bash
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.
