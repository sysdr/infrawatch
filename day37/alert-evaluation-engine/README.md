# Alert Evaluation Engine

A comprehensive alert evaluation system that processes metrics in real-time and generates intelligent alerts using threshold monitoring, anomaly detection, and deduplication.

## Features

- **Rule Evaluation Engine**: Supports threshold, anomaly, and composite rule types
- **Anomaly Detection**: Statistical, ML-based, and seasonal pattern detection
- **Smart Deduplication**: Prevents alert storms and reduces noise
- **Real-time Dashboard**: WordPress-inspired UI for monitoring and management
- **Scalable Architecture**: Built for high-throughput metric processing

## Quick Start

1. **Build the application:**
   ```bash
   ./build.sh
   ```

2. **Start all services:**
   ```bash
   ./start.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Stop the application:**
   ```bash
   ./stop.sh
   ```

## Architecture

- **Backend**: FastAPI with async processing
- **Frontend**: React with Material-UI
- **Database**: PostgreSQL for persistence
- **Cache**: Redis for deduplication and performance
- **Monitoring**: Built-in metrics and observability

## Testing

```bash
# Backend tests
cd backend
source venv/bin/activate
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## Docker Support

Run with Docker Compose:
```bash
docker-compose -f docker/docker-compose.yml up
```

## Components

- **Rule Evaluator**: Core evaluation logic
- **Alert Generator**: Creates and manages alert instances
- **Deduplicator**: Prevents duplicate alerts
- **Dashboard**: Real-time monitoring interface
- **Rules Manager**: Configure and manage alert rules
- **Alerts View**: Monitor active alerts

Built for the "180-Day Hands-On Full Stack Development" series - Day 37.
