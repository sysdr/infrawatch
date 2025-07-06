# Auth Testing Suite

A comprehensive authentication testing environment with FastAPI backend, React frontend, PostgreSQL database, and Redis caching.

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Running the Demo

1. **Start all services:**
   ```bash
   ./demo.sh
   ```

2. **Stop all services:**
   ```bash
   ./stop.sh
   ```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React application |
| Backend API | 8000 | FastAPI authentication service |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Caching and sessions |

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/api/health
- **API Documentation**: http://localhost:8000/docs

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Frontend   │    │   Backend   │    │ PostgreSQL  │
│   (React)   │◄──►│   (FastAPI) │◄──►│  Database   │
│   Port 3000 │    │  Port 8000  │    │  Port 5432  │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │    Redis    │
                   │   Cache &   │
                   │  Sessions   │
                   │  Port 6379  │
                   └─────────────┘
```

## Development

### Backend (FastAPI)

- **Location**: `backend/`
- **Dependencies**: See `backend/requirements.txt`
- **Main file**: `backend/app/main.py`

### Frontend (React + TypeScript)

- **Location**: `frontend/`
- **Dependencies**: See `frontend/package.json`
- **Build tool**: Vite

## Docker Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access containers
```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh

# Database
docker-compose exec postgres psql -U postgres -d auth_testing
```

### Rebuild specific service
```bash
docker-compose build backend
docker-compose up -d backend
```

## Environment Variables

The following environment variables are configured in `docker-compose.yml`:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `DEBUG`: Debug mode flag

## Troubleshooting

### Port conflicts
If you get port conflicts, check if services are already running:
```bash
docker ps
```

### Database issues
Reset the database:
```bash
docker-compose down -v
docker-compose up -d
```

### Build issues
Clean and rebuild:
```bash
docker-compose down
docker system prune -f
./demo.sh
```

## Testing

The backend includes comprehensive testing with pytest:

```bash
# Run tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Health Check
- `GET /api/health` - Service health status

## Contributing

1. Make changes to the code
2. Rebuild the affected service: `docker-compose build <service>`
3. Restart the service: `docker-compose up -d <service>`
4. Test your changes

## License

This project is for testing and development purposes. 