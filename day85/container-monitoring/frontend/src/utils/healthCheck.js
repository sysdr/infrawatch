// Health check utility for backend
// Try proxy first, fallback to direct connection if proxy fails
export async function checkBackendHealth() {
  // Try proxy first (in development)
  if (import.meta.env.DEV) {
    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })
      if (response.ok) {
        const data = await response.json()
        return { healthy: true, data }
      }
    } catch (error) {
      // Proxy failed, try direct connection
      console.warn('Proxy health check failed, trying direct connection:', error.message)
    }
  }
  
  // Fallback to direct connection
  try {
    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      mode: 'cors', // Explicitly request CORS
    })
    if (response.ok) {
      const data = await response.json()
      return { healthy: true, data }
    }
    return { healthy: false, error: `HTTP ${response.status}` }
  } catch (error) {
    return { healthy: false, error: error.message }
  }
}

export async function testWebSocketConnection(url) {
  return new Promise((resolve) => {
    const ws = new WebSocket(url)
    const timeout = setTimeout(() => {
      ws.close()
      resolve({ connected: false, error: 'Connection timeout' })
    }, 3000)

    ws.onopen = () => {
      clearTimeout(timeout)
      ws.close()
      resolve({ connected: true })
    }

    ws.onerror = (error) => {
      clearTimeout(timeout)
      resolve({ connected: false, error: 'WebSocket connection failed' })
    }
  })
}
