# Day 67: Interactive Dashboard Features

Production-grade interactive dashboard with drill-down, zoom, time range selection, and cross-filtering.

## Quick Start

### Without Docker

1. Install dependencies:
```bash
./scripts/build.sh
```

2. Start PostgreSQL and Redis

3. Run application:
```bash
./scripts/start.sh
```

### With Docker

```bash
docker-compose up --build
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features

- ✅ Drill-down navigation through service → endpoint → region
- ✅ Temporal and data zoom on charts
- ✅ Time range presets (15m, 1h, 6h, 24h, 7d)
- ✅ Dynamic filter controls with progressive loading
- ✅ Cross-filtering - selecting in one chart filters all others
- ✅ Redis caching for performance
- ✅ PostgreSQL with optimized indexes

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/
```
