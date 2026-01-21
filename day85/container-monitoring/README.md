# Container Monitoring System

Production-grade Docker container monitoring with real-time metrics, health checks, and lifecycle tracking.

## Features

- Real-time container metrics (CPU, memory, network, disk I/O)
- Docker health check integration
- Container lifecycle event tracking
- Anomaly detection with baseline learning
- WebSocket-based live updates
- Professional dashboard UI

## Quick Start

### Build
```bash
./build.sh
```

### Run (Docker)
```bash
docker-compose -f docker/docker-compose.yml up
```

### Run (Local)
Terminal 1:
```bash
cd backend && source venv/bin/activate && uvicorn backend.app.main:app --reload
```

Terminal 2:
```bash
cd frontend && npm run dev
```

### Access
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Testing
```bash
cd backend
source venv/bin/activate
pytest tests/
```

## Architecture

- Backend: FastAPI + Docker SDK
- Frontend: React + Material-UI + Recharts
- Real-time: WebSockets
- Monitoring: 1-second metric updates

## Requirements

- Docker access (/var/run/docker.sock)
- Python 3.11+
- Node.js 20+
