# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/src/ ./src/
COPY backend/tests/ ./tests/

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port for web server
EXPOSE 8000

# Run the application
CMD ["python", "src/main.py"]