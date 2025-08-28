# Day 25: Metrics Aggregation System

A comprehensive real-time metrics aggregation system built with Python FastAPI backend and React frontend.

## Features

- **Real-time Aggregation Engine**: Process metrics as they arrive with sliding time windows
- **Statistical Calculations**: Compute percentiles, standard deviation, and trend analysis
- **Historical Rollups**: Automatic data aggregation at multiple time granularities
- **Live Dashboard**: Real-time visualization with WebSocket updates
- **Performance Optimization**: Efficient memory management and parallel processing

## Quick Start

### Using Docker (Recommended)
```bash
./start.sh
```

### Manual Setup
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## Architecture

The system consists of:

1. **Aggregation Engine**: Real-time metric processing with time windows
2. **Rollup Manager**: Historical data compression and retention
3. **Statistical Calculator**: Advanced statistical computations
4. **Time-series Storage**: Efficient data storage and retrieval
5. **REST API**: Query interface for aggregated data
6. **WebSocket API**: Real-time data streaming
7. **React Dashboard**: Interactive visualization interface

## API Endpoints

- `GET /api/v1/metrics/current` - Current aggregated metrics
- `GET /api/v1/metrics/summary` - Aggregation engine summary
- `GET /api/v1/metrics/trends/{metric_name}` - Trend analysis
- `GET /api/v1/rollups/status` - Rollup system status
- `POST /api/v1/rollups/trigger` - Manual rollup trigger
- `GET /api/v1/statistics/calculate` - Statistical calculations

## Dashboard Access

- **Main Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

## Performance

- Handles 10,000+ metrics/second
- Sub-100ms aggregation latency
- Automatic memory management
- Configurable retention policies

## Stop System

```bash
./stop.sh
```
