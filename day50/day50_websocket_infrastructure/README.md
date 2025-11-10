# Day 50: WebSocket Infrastructure

Production-grade WebSocket infrastructure with Socket.IO, connection management, authentication, and room-based messaging.

## Quick Start

### Without Docker:
```bash
./build.sh
```

### With Docker:
```bash
./build.sh docker
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/health

## Testing

### Multiple Clients:
1. Open http://localhost:3000 in multiple browser tabs
2. Login with different usernames
3. Join the same room in each tab
4. Send messages to see real-time communication

### Features to Test:
- ✅ Connection authentication
- ✅ Automatic reconnection
- ✅ Room management
- ✅ Real-time messaging
- ✅ Connection statistics

## Stopping Services

```bash
./stop.sh
```

## Project Structure

```
backend/
  src/
    server.py          # WebSocket server
  tests/
    test_server.py     # Unit tests
frontend/
  src/
    components/        # React components
    services/          # Socket service
    hooks/            # Custom hooks
```
