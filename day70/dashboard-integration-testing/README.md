# Day 70: Dashboard Integration Testing

## Quick Start

### Option 1: Automated Build (30 minutes)
```bash
./build.sh
```

### Option 2: Docker (Recommended for Production)
```bash
docker-compose up --build
```

### Option 3: Manual Build

1. Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend:
```bash
cd frontend
npm install
npm run dev
```

3. Start Redis:
```bash
redis-server
```

## Testing

### Integration Tests
```bash
cd backend
source venv/bin/activate
pytest tests/integration/ -v
```

### Performance Tests
```bash
cd tests
locust -f performance_test.py --headless --users 100 --spawn-rate 10 --run-time 60s --host http://localhost:8000
```

## Access Points

- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Features Demonstrated

✅ Real-time metric streaming via WebSocket  
✅ Batched updates (16ms window for 60fps)  
✅ Priority message handling  
✅ Performance monitoring  
✅ Load simulation (Normal/High/Burst)  
✅ Responsive design (mobile/tablet/desktop)  
✅ Integration testing  
✅ Performance testing with Locust  

## Architecture

- Backend: FastAPI + WebSocket + Redis
- Frontend: React 18 + Material-UI + Recharts
- Testing: Pytest + Locust + Playwright
- Deployment: Docker + Docker Compose
