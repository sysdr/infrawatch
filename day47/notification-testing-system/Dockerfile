# Multi-stage build for Python backend and React frontend

# Backend stage
FROM python:3.11-slim as backend-build

WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Frontend stage  
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend
COPY frontend/package.json .
RUN npm install

COPY frontend/ .
RUN npm run build

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Serve frontend static files from backend
RUN mkdir -p backend/static
RUN cp -r frontend/build/* backend/static/

EXPOSE 8000

CMD ["python", "backend/src/main.py"]
