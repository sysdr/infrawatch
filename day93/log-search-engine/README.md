# Day 93: Log Search Engine

A production-grade log search engine with custom query language, multiple indexing strategies, and real-time search capabilities.

## Features

- Custom query language with field queries, ranges, wildcards, and boolean operators
- Multiple indexing strategies (inverted index, trigram matching, GIN indexes)
- Real-time search with WebSocket support
- Performance optimization with Redis caching
- Faceted search
- Search analytics
- Modern React UI with Ant Design

## Quick Start

### With Docker
```bash
cd log-search-engine
./build.sh --docker
```

### Without Docker
```bash
cd log-search-engine
./build.sh
```

## Access

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Query Language Examples

- `level:error` - Field query
- `service:api AND level:error` - Boolean AND
- `level:error OR level:critical` - Boolean OR
- `message:*timeout*` - Wildcard search
- `timestamp:[2025-01-01 TO 2025-01-31]` - Range query
- `NOT level:info` - Negation

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v

# Performance testing
locust -f tests/test_performance.py --host=http://localhost:8000
```

## Stop Services

```bash
./stop.sh
```
