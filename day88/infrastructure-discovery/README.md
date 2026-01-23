# Infrastructure Discovery System

Day 88: Production-grade infrastructure discovery and management system.

## Features

- **Automatic Discovery**: Continuously discovers cloud resources
- **Inventory Management**: Real-time resource tracking and cataloging
- **Topology Mapping**: Visual representation of infrastructure relationships
- **Dependency Tracking**: Understand resource dependencies and impact
- **Change Detection**: Track configuration drift and modifications

## Quick Start

### With Docker

```bash
cd docker
docker-compose up
```

### Without Docker

```bash
# Build
./scripts/build.sh

# Start
./scripts/start.sh

# Test
./scripts/test.sh

# Stop
./scripts/stop.sh
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture

- Backend: Python FastAPI
- Frontend: React with D3.js
- Database: PostgreSQL
- Cache: Redis
- Container: Docker

## Testing

Run comprehensive tests:
```bash
./scripts/test.sh
```

## License

MIT License - Day 88 Infrastructure Discovery System
