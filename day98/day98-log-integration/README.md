# Day 98: Log Management Integration

Production-grade log pipeline with hot/warm/cold data paths, real-time WebSocket streaming, automated retention policies, and security correlation.

## Architecture

Three parallel data paths:
- **Hot Path**: Redis Streams → WebSocket (real-time)
- **Warm Path**: Elasticsearch bulk indexing (searchable)
- **Cold Path**: S3 tiered storage (archival)

## Features

✅ Real-time log streaming via WebSocket
✅ Full-text search with Elasticsearch
✅ Automated retention policies
✅ Security pattern correlation
✅ Performance monitoring dashboard

## Quick Start

```
./build.sh
```

This starts:
- Backend API (port 8000)
- WebSocket server
- Background workers (indexer, retention, security)
- Frontend dashboard (port 3000)
- Redis and Elasticsearch (if using Docker)

### Access

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Test

Generate test logs:
```
python3 scripts/generate_test_logs.py 100 10
```

Simulate brute force attack:
```
python3 scripts/simulate_brute_force.py testuser 10 5
```

### Stop

```
./stop.sh
```

## Project Structure

```
day98-log-integration/
├── backend/
│   ├── api/
│   ├── workers/
│   ├── models/
│   └── utils/
├── frontend/
│   └── src/
│       └── components/
├── tests/
├── docker/
└── scripts/
```

## Technologies

- Backend: FastAPI, Python 3.11
- Frontend: React 18, Material-UI
- Storage: Redis, Elasticsearch, S3 (mock)
- Deployment: Docker Compose
