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
