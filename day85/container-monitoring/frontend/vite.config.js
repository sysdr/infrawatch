import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: false, // Allow Vite to use next available port if 3000 is taken
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true, // Enable WebSocket proxying for /api routes
        secure: false,
        rewrite: (path) => {
          // Remove /api prefix and forward to backend
          // /api/health -> /health
          // /api/v1/containers -> /api/v1/containers
          if (path.startsWith('/api/health')) {
            return path.replace('/api', '')
          }
          return path
        },
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('Proxy error:', err);
          });
          proxy.on('proxyReqWs', (proxyReq, req, socket) => {
            console.log('WebSocket proxy request:', req.url);
          });
          proxy.on('upgrade', (req, socket, head) => {
            console.log('WebSocket upgrade:', req.url);
          });
        }
      }
    }
  }
})
