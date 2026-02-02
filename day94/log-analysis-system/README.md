# Day 94: Log Analysis System

Production-grade log analysis system with pattern recognition, anomaly detection, trend analysis, alert generation, and real-time visualization.

## Features

- **Pattern Recognition**: Automatic identification of log structures
- **Anomaly Detection**: Z-score, moving average, and isolation forest algorithms
- **Trend Analysis**: Time-series decomposition and prediction
- **Alert Management**: Intelligent routing with deduplication
- **Real-time Dashboards**: WebSocket-powered live updates

## Quick Start

### With Docker
```bash
./build.sh docker
```

### Without Docker
```bash
# Ensure PostgreSQL and Redis are running
./build.sh
```

## Access

- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Testing

Run the simulator in the dashboard to generate test data and see the system in action.

## Performance Targets

- Process 50,000 logs/second
- Detect anomalies within 5 seconds
- Generate alerts within 100ms
- 95%+ anomaly detection accuracy

## Architecture

- Backend: FastAPI + Python
- Frontend: React
- Database: PostgreSQL
- Cache: Redis
- Real-time: WebSockets

Built for Day 94 of 180-Day Full Stack Development Series
