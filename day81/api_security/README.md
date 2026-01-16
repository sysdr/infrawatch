# Day 81: API Security System

## Overview
Production-grade API security implementation with rate limiting, API key management, request signing, IP whitelisting, and security headers.

## Features
- Token bucket rate limiting with Redis
- API key lifecycle management
- HMAC-SHA256 request signing
- CIDR-based IP whitelisting
- OWASP security headers
- Real-time monitoring dashboard

## Quick Start

### With Docker
```bash
./build.sh docker
```

### Without Docker
```bash
# Install PostgreSQL 16 and Redis 7
./build.sh
```

## Architecture
- Backend: FastAPI + PostgreSQL + Redis
- Frontend: React + Ant Design
- Rate Limiting: Token bucket algorithm
- Authentication: API key + HMAC signing

## API Endpoints
- `POST /admin/api-keys` - Create API key
- `GET /admin/api-keys` - List keys
- `DELETE /admin/api-keys/{key_id}` - Revoke key
- `POST /admin/api-keys/{key_id}/rotate` - Rotate key
- `GET /admin/request-logs` - View logs
- `GET /admin/analytics/rate-limits` - Analytics

## Testing
```bash
cd backend
source venv/bin/activate
pytest ../tests -v
```

## Security Mechanisms

### Rate Limiting
- Algorithm: Token bucket
- Storage: Redis sorted sets
- Response: 429 with Retry-After header

### Request Signing
- Algorithm: HMAC-SHA256
- Headers: X-Signature, X-Timestamp
- Replay protection: 5-minute window

### IP Whitelisting
- Format: CIDR notation
- Validation: Pre-request
- Cache: Redis (5-min TTL)

## Performance Targets
- Rate limit check: <5ms
- Signature verification: <10ms
- IP check: <2ms
- Total overhead: <20ms

## Stop
```bash
./stop.sh
```
