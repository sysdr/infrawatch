# Day 51: Real-time Data Streaming

Production-grade real-time streaming system with WebSocket, metrics collection, alert broadcasting, and intelligent throttling.

## Features

- Live metric streaming (CPU, Memory, Disk)
- Alert broadcasting with priority levels
- Connection performance optimization
- Data throttling and backpressure handling
- Compression for large payloads
- Heartbeat protocol
- Automatic reconnection

## Quick Start

### Without Docker
```bash
./build.sh
```

### With Docker
```bash
./build.sh --docker
```

### Stop Services
```bash
./stop.sh              # Without Docker
./stop.sh --docker     # With Docker
```

## Access

- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture

- Backend: Python + FastAPI + Socket.IO
- Frontend: React + Socket.IO Client + Recharts
- Real-time WebSocket streaming
- Intelligent throttling and batching

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app
```

## Assignment

Build a streaming stock ticker with price updates, alerts, and replay feature.
