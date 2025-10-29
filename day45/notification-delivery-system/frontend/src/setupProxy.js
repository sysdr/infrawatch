const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy API requests
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
    })
  );

  // Proxy WebSocket connections
  app.use(
    '/ws',
    createProxyMiddleware({
      target: 'ws://localhost:8000',
      ws: true,
      changeOrigin: true,
      headers: {
        'Origin': 'http://localhost:8000',
        'Host': 'localhost:8000'
      }
    })
  );
};
