const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  const backend = 'http://localhost:8000';
  // Avoid favicon 404: serve favicon.svg when browser requests favicon.ico
  app.get('/favicon.ico', (req, res) => res.redirect(302, '/favicon.svg'));
  // API HTTP requests
  app.use(
    '/api',
    createProxyMiddleware({
      target: backend,
      changeOrigin: true,
    })
  );
  // WebSocket (same origin so no 403)
  app.use(
    '/ws',
    createProxyMiddleware({
      target: backend,
      changeOrigin: true,
      ws: true,
    })
  );
};
