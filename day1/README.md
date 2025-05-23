# InfraWatch - Infrastructure Monitoring Platform

A distributed systems learning project that demonstrates real-time infrastructure monitoring.

## Architecture
- **Backend**: Node.js REST API with Express
- **Frontend**: Real-time monitoring dashboard
- **Containerization**: Docker and Docker Compose

## Getting Started

### Without Docker
1. Install backend dependencies: `cd backend && npm install`
2. Start backend: `npm start`
3. Open frontend: Open `frontend/public/index.html` in browser

### With Docker
1. Build and run: `docker-compose up --build`
2. Access dashboard: http://localhost:3000

## API Endpoints
- `GET /health` - Service health check
- `GET /api/infrastructure/status` - Infrastructure status data
