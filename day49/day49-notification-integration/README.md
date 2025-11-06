# Day 49: Notification System Integration

## Quick Start

### With Docker (Recommended)
```bash
./build.sh --docker
```

### Without Docker (Requires local PostgreSQL and Redis)
```bash
# Install PostgreSQL and Redis first
./build.sh
```

## Access

- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## Testing

```bash
cd tests
pytest test_integration.py -v
```

## Stop Services

```bash
./stop.sh
```

## Features

- ✅ Alert creation and management
- ✅ Multi-channel notifications (Email, SMS, Slack)
- ✅ User preference management
- ✅ Circuit breaker pattern
- ✅ Idempotency guarantees
- ✅ Escalation policies
- ✅ Real-time dashboard
- ✅ Notification history and auditing

## Architecture

- **Backend**: FastAPI + SQLAlchemy + Redis
- **Frontend**: React + Vite + TailwindCSS
- **Database**: PostgreSQL
- **Cache**: Redis
- **Notification Providers**: Email, SMS, Slack simulation
