# Report Templates System

Production-ready report template system with dynamic generation, scheduling, and email delivery.

## Features
- Template management with version control
- Dynamic report generation with Jinja2
- Scheduled reports with cron expressions
- Email delivery with SendGrid
- HTML and PDF output formats
- Real-time execution tracking

## Quick Start

### Local Development
```bash
./build.sh local
```

### With Docker
```bash
./build.sh docker
```

### Access Points
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Running Demo
```bash
./demo.sh
```

## Testing
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Stop Services
```bash
./stop.sh
```
