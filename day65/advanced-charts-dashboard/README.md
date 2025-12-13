# Day 65: Advanced Chart Components

Production-grade chart visualization system with multi-series, stacked, scatter, heatmap, and custom chart types.

## Quick Start

### Without Docker
```bash
./build.sh
```

Visit http://localhost:3000 to see the dashboard.

### With Docker
```bash
docker-compose up --build
```

## Features

- **Multi-Series Charts**: Time-series with multiple metrics, brush selection, zoom
- **Stacked Charts**: Bar and area charts with cumulative values
- **Scatter Plots**: Correlation analysis with outlier detection
- **Heatmaps**: Temporal pattern visualization with D3
- **Custom Charts**: Latency distribution box plots, status timelines

## API Endpoints

- `GET /api/charts/multi-series` - Multi-series time-series data
- `GET /api/charts/stacked` - Stacked bar/area data
- `GET /api/charts/scatter` - Scatter plot with correlation
- `GET /api/charts/heatmap` - Heatmap temporal data
- `GET /api/charts/custom/latency-distribution` - Box plot data
- `GET /api/charts/custom/status-timeline` - Service status events

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov
```

## Stop Services

```bash
./stop.sh
```
