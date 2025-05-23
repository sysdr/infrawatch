# Create backend package.json - this defines our service dependencies
cat > backend/package.json << 'EOF'
{
  "name": "infrawatch-backend",
  "version": "1.0.0",
  "description": "Infrastructure monitoring backend service",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js",
    "test": "jest",
    "docker:build": "docker build -t infrawatch-backend .",
    "docker:run": "docker run -p 3001:3001 infrawatch-backend"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.7.0"
  }
}
EOF

# Create the main server file - this is your API gateway
cat > backend/src/server.js << 'EOF'
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware setup - essential for distributed systems communication
app.use(cors());
app.use(express.json());

// Health check endpoint - critical for load balancers and monitoring
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'infrawatch-backend',
    version: '1.0.0'
  });
});

// Infrastructure status endpoint - simulates real monitoring data
app.get('/api/infrastructure/status', (req, res) => {
  res.json({
    services: [
      { name: 'Database', status: 'running', uptime: '99.9%' },
      { name: 'Cache', status: 'running', uptime: '99.8%' },
      { name: 'Load Balancer', status: 'running', uptime: '100%' },
      { name: 'API Gateway', status: 'running', uptime: '99.95%' }
    ],
    timestamp: new Date().toISOString(),
    totalRequests: Math.floor(Math.random() * 1000000),
    responseTime: Math.floor(Math.random() * 100) + 'ms'
  });
});

// Start server with proper error handling
app.listen(PORT, () => {
  console.log(`🚀 InfraWatch Backend running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`📈 Status API: http://localhost:${PORT}/api/infrastructure/status`);
});
EOF

# Create frontend dashboard
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InfraWatch Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f1419; color: #e6e6e6; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { color: #00d4aa; font-size: 2.5em; margin-bottom: 10px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; }
        .status-card { background: linear-gradient(135deg, #1e2328 0%, #2d3748 100%); padding: 25px; border-radius: 12px; border-left: 5px solid #00d4aa; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); }
        .status-healthy { border-left-color: #00d4aa; }
        .status-warning { border-left-color: #ffd700; }
        .status-error { border-left-color: #ff6b6b; }
        .card-title { font-size: 1.4em; margin-bottom: 15px; color: #ffffff; }
        .card-content p { margin: 8px 0; font-size: 1.1em; }
        .loading { text-align: center; color: #888; font-size: 1.2em; }
        .metrics-bar { background: #1a202c; padding: 20px; border-radius: 8px; margin-bottom: 30px; display: flex; justify-content: space-around; }
        .metric { text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #00d4aa; }
        .metric-label { color: #a0aec0; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 InfraWatch</h1>
            <p>Real-time Infrastructure Monitoring Dashboard</p>
        </div>
        
        <div id="metrics-container"></div>
        <div id="status-container" class="loading">Loading infrastructure status...</div>
    </div>

    <script>
        // Global variables to track system state
        let refreshInterval;
        let lastUpdateTime;

        async function loadInfrastructureStatus() {
            try {
                const response = await fetch('http://localhost:3001/api/infrastructure/status');
                const data = await response.json();
                
                // Update metrics bar
                const metricsContainer = document.getElementById('metrics-container');
                metricsContainer.innerHTML = `
                    <div class="metrics-bar">
                        <div class="metric">
                            <div class="metric-value">${data.services.length}</div>
                            <div class="metric-label">Services</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.totalRequests.toLocaleString()}</div>
                            <div class="metric-label">Total Requests</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.responseTime}</div>
                            <div class="metric-label">Avg Response</div>
                        </div>
                    </div>
                `;
                
                // Update status cards
                const container = document.getElementById('status-container');
                container.innerHTML = `
                    <div class="status-grid">
                        ${data.services.map(service => `
                            <div class="status-card status-healthy">
                                <h3 class="card-title">${service.name}</h3>
                                <div class="card-content">
                                    <p><strong>Status:</strong> ${service.status}</p>
                                    <p><strong>Uptime:</strong> ${service.uptime}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <p style="text-align: center; margin-top: 30px; color: #64748b;">
                        🕒 Last updated: ${new Date(data.timestamp).toLocaleString()}
                    </p>
                `;
                
                lastUpdateTime = new Date();
            } catch (error) {
                document.getElementById('status-container').innerHTML = 
                    '<div style="text-align: center; color: #ff6b6b; font-size: 1.2em;">⚠️ Failed to load infrastructure status<br>Please ensure backend is running on port 3001</div>';
            }
        }

        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', function() {
            loadInfrastructureStatus();
            // Refresh every 10 seconds for real-time feeling
            refreshInterval = setInterval(loadInfrastructureStatus, 10000);
        });
    </script>
</body>
</html>
EOF

# Create Docker configurations
cat > backend/Dockerfile << 'EOF'
# Use Node.js Alpine for smaller image size - important for distributed systems
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package*.json ./

# Install dependencies
RUN npm install --only=production

# Copy application code
COPY . .

# Expose the port our app runs on
EXPOSE 3001

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# Start the application
CMD ["npm", "start"]
EOF

cat > frontend/Dockerfile << 'EOF'
# Use nginx for serving static files - common in production
FROM nginx:alpine

# Copy our HTML files to nginx serve directory
COPY public /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Nginx starts automatically in the base image
EOF

# Create docker-compose for orchestration
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Backend API service
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
      - PORT=3001
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  # Frontend dashboard service
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy

# Create a custom network for service communication
networks:
  default:
    name: infrawatch-network
EOF

# Create comprehensive .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
dist/
build/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed
*.pid.lock
EOF

# Create project README
cat > README.md << 'EOF'
# InfraWatch - Infrastructure Monitoring Platform

A distributed systems learning project that demonstrates real-time infrastructure monitoring.

## Architecture
- **Backend**: Node.js REST API with Express
- **Frontend**: Real-time monitoring dashboard
- **Containerization**: Docker and Docker Compose

## Getting Started

### Without Docker
1. Install backend dependencies: `cd backend && npm install`
2. Start backend: `npm start`
3. Open frontend: Open `frontend/public/index.html` in browser

### With Docker
1. Build and run: `docker-compose up --build`
2. Access dashboard: http://localhost:3000

## API Endpoints
- `GET /health` - Service health check
- `GET /api/infrastructure/status` - Infrastructure status data
EOF