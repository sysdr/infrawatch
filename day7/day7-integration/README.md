
## Docker Setup

To run the application using Docker:

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. Stop the containers:
   ```bash
   docker-compose down
   ```

The application includes:
- Frontend (React) served by Nginx
- Backend (FastAPI) with health checks
- Redis for caching and session management
