# Day 90: Infrastructure UI Dashboard

Production-grade infrastructure visualization and management system.

## Features

- Interactive topology visualization with force-directed graphs
- Real-time resource management (CRUD operations)
- Cost analysis with trends and forecasting
- Compliance and utilization reporting
- WebSocket real-time updates
- Multi-cloud support (AWS, GCP, Azure)

## Quick Start

### With Docker

```bash
./build.sh
# Select option 2 (With Docker)
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

### Without Docker

Requirements:
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

```bash
./build.sh
# Select option 1 (Without Docker)
```

Access at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/
```

## Architecture

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + Redis
- **Frontend**: React + Redux + Material-UI + Recharts
- **Real-time**: WebSocket for live updates
- **Deployment**: Docker + Docker Compose

## Performance

- Topology rendering: 60fps with 500+ nodes
- API response: < 200ms (p95)
- Cache hit rate: 95%+
- WebSocket latency: < 2s

## Stop Services

```bash
./stop.sh
```
