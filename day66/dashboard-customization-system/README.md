# Dashboard Customization System - Day 66

A production-grade dashboard customization platform with real-time collaboration features.

## Features

- **Widget Configuration**: Dynamic widget settings with real-time preview
- **Multi-Theme Support**: Light, dark, ocean, and sunset themes
- **Layout Persistence**: Save, load, and version dashboard configurations
- **Sharing**: Secure dashboard sharing with granular permissions
- **Real-time Updates**: WebSocket-based collaboration
- **Template Library**: Pre-built dashboard templates

## Quick Start

### With Docker
```bash
./build.sh
```

### Without Docker
Requirements:
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

```bash
./build.sh
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Demo Credentials

- Email: demo@example.com
- Password: demo123

## Testing

Backend tests:
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

Frontend tests:
```bash
cd frontend
npm test
```

## Stop System

```bash
./stop.sh
```

## Architecture

- **Backend**: FastAPI + PostgreSQL + Redis + WebSocket
- **Frontend**: React + Material-UI + Socket.IO
- **Deployment**: Docker Compose

## Key Patterns

- Schema-based widget configuration
- CSS variable-based theming
- Optimistic locking for concurrent edits
- Redis caching with version-based invalidation
- WebSocket rooms for real-time collaboration
