import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3130, host: true,
    proxy: { '/api': { target: 'http://localhost:8130', changeOrigin: true } }
  }
})
