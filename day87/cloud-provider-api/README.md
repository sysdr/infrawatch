# Day 87: Cloud Provider APIs

Production-grade cloud infrastructure management system with AWS SDK integration.

## Features

- Real-time resource discovery across AWS regions
- Live cost tracking and forecasting
- Multi-dimensional health monitoring
- Auto-scaling event tracking
- Professional React dashboard

## Quick Start

### With Docker (Recommended)

```bash
./build.sh --docker
```

### Without Docker

Prerequisites:
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- AWS credentials configured

```bash
./build.sh
```

## Testing

```bash
./test.sh
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## AWS Configuration

Set AWS credentials as environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

Or use AWS CLI configured credentials.

## Architecture

- Backend: FastAPI + Python
- Frontend: React + Material-UI
- Database: PostgreSQL
- Cache: Redis
- Cloud: AWS SDK (boto3)

## Stop Services

```bash
./stop.sh
```
