import { useEffect, useState, useRef } from 'react'

// Get WebSocket URL - use relative URL for Vite proxy, or absolute for direct connection
const getWebSocketUrl = (path) => {
  // In development with Vite proxy, use relative URL that goes through proxy
  if (import.meta.env.DEV) {
    // Vite proxy handles /api routes, so use relative URL
    // This ensures WebSocket goes through Vite's proxy
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host // Includes port (e.g., localhost:3001)
    return `${protocol}//${host}${path}`
  }
  // In production, use configured backend URL or default
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'ws://localhost:8000'
  return `${backendUrl}${path}`
}

export function useWebSocket({ onMetrics, onEvent }) {
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)
  const wsMetrics = useRef(null)
  const wsEvents = useRef(null)
  const isMounted = useRef(true)
  const isCleaningUp = useRef(false)
  const callbacksRef = useRef({ onMetrics, onEvent })
  const retryCount = useRef({ metrics: 0, events: 0 })
  const retryTimeouts = useRef({ metrics: null, events: null })

  // Update callbacks ref without causing re-renders
  useEffect(() => {
    callbacksRef.current = { onMetrics, onEvent }
  }, [onMetrics, onEvent])

  // Helper function to safely close WebSocket
  const safeClose = (ws, name) => {
    if (!ws) return
    
    const readyState = ws.readyState
    
    // Always remove all event handlers first to prevent error callbacks during cleanup
    // This is the key to preventing error logs during React StrictMode cleanup
    try {
      ws.onopen = null
      ws.onmessage = null
      ws.onerror = null
      ws.onclose = null
    } catch (e) {
      // Ignore errors when removing handlers
    }
    
    // Only close if the WebSocket is already open
    // If it's still CONNECTING, removing handlers is enough - the connection will fail silently
    // Closing a CONNECTING WebSocket causes browser console errors
    if (readyState === WebSocket.OPEN) {
      try {
        ws.close(1000, 'Component unmounting')
      } catch (e) {
        // Silently ignore errors during cleanup
      }
    }
    // For CONNECTING, CLOSING, or CLOSED states, we've already removed handlers
    // so no further action is needed
  }

  useEffect(() => {
    isMounted.current = true
    isCleaningUp.current = false
    let metricsConnected = false
    let eventsConnected = false
    let metricsTimeoutId = null
    let eventsTimeoutId = null

    // Helper to create metrics WebSocket with retry logic
    const connectMetrics = (isRetry = false, useDirect = false) => {
      // Double-check we're still mounted before creating WebSocket
      if (!isMounted.current || isCleaningUp.current) return
      
      // Clear any pending retry
      if (retryTimeouts.current.metrics) {
        clearTimeout(retryTimeouts.current.metrics)
        retryTimeouts.current.metrics = null
      }
      
      try {
        // Use direct connection to backend for WebSockets
        // WebSocket proxying through Vite can be unreliable, so connect directly
        let url
        if (useDirect || import.meta.env.DEV) {
          // Direct connection to backend (preferred for WebSockets)
          url = 'ws://localhost:8000/api/v1/ws/metrics'
          console.log('Using direct connection to:', url)
        } else {
          // In production, use configured backend URL
          const backendUrl = import.meta.env.VITE_BACKEND_URL || 'ws://localhost:8000'
          url = `${backendUrl}/api/v1/ws/metrics`
          console.log('Using backend URL:', url)
        }
        
        wsMetrics.current = new WebSocket(url)
        
        wsMetrics.current.onopen = () => {
          if (isMounted.current && !isCleaningUp.current) {
            console.log('Metrics WebSocket connected')
            retryCount.current.metrics = 0 // Reset retry count on success
            metricsConnected = true
            // Set connected if metrics is connected (events is optional)
            setConnected(true)
            setError(null)
          }
        }
        
        wsMetrics.current.onmessage = (event) => {
          if (!isMounted.current || isCleaningUp.current) return
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'connected') {
              console.log('Metrics WebSocket:', data.message)
              // Connection confirmed
            } else if (data.type === 'metrics' && callbacksRef.current.onMetrics) {
              callbacksRef.current.onMetrics(data.data)
            } else if (data.type === 'ping' || data.type === 'pong') {
              // Keepalive messages, ignore
            }
          } catch (e) {
            console.error('Error parsing metrics:', e)
          }
        }
        
        wsMetrics.current.onerror = (error) => {
          // Suppress errors during cleanup or if not mounted
          if (!isMounted.current || isCleaningUp.current) return
          console.error('Metrics WebSocket error event:', error)
          // Set error state but don't set connected to false yet - let onclose handle it
          if (!metricsConnected) {
            setError('Failed to connect to metrics stream. Check if backend is running on port 8000.')
          }
        }
        
        wsMetrics.current.onclose = (event) => {
          // Suppress logs during cleanup
          if (!isMounted.current || isCleaningUp.current) return
          
          metricsConnected = false
          setConnected(false)
          
          // Only retry if it wasn't a normal closure and we haven't exceeded max retries
          if (event.code !== 1000 && event.code !== 1001) {
            const maxRetries = 5
            if (retryCount.current.metrics < maxRetries) {
              retryCount.current.metrics++
              const delay = Math.min(1000 * Math.pow(2, retryCount.current.metrics - 1), 10000) // Exponential backoff, max 10s
              
              console.log(`Metrics WebSocket disconnected (${event.code}). Retrying in ${delay}ms... (${retryCount.current.metrics}/${maxRetries})`)
              setError(`Connecting to metrics stream... (attempt ${retryCount.current.metrics}/${maxRetries})`)
              
              retryTimeouts.current.metrics = setTimeout(() => {
                if (isMounted.current && !isCleaningUp.current) {
                  connectMetrics(true)
                }
              }, delay)
            } else {
              // Already using direct connection, so connection failed
              console.error('Metrics WebSocket: Max retries reached. Connection failed.')
              setError('Failed to connect to metrics stream. Please ensure the backend server is running on port 8000.')
            }
          } else if (event.code === 1000) {
            console.log('Metrics WebSocket closed normally')
            setError(null)
          }
        }
      } catch (e) {
        if (isMounted.current && !isCleaningUp.current) {
          console.error('Error creating metrics WebSocket:', e)
          setError('Failed to create metrics WebSocket connection. Please check your network settings.')
        }
      }
    }

    // Helper to create events WebSocket with retry logic
    const connectEvents = (isRetry = false, useDirect = false) => {
      // Double-check we're still mounted before creating WebSocket
      if (!isMounted.current || isCleaningUp.current) return
      
      // Clear any pending retry
      if (retryTimeouts.current.events) {
        clearTimeout(retryTimeouts.current.events)
        retryTimeouts.current.events = null
      }
      
      try {
        // Use direct connection to backend for WebSockets
        // WebSocket proxying through Vite can be unreliable, so connect directly
        let url
        if (useDirect || import.meta.env.DEV) {
          // Direct connection to backend (preferred for WebSockets)
          url = 'ws://localhost:8000/api/v1/ws/events'
          console.log('Using direct connection to:', url)
        } else {
          // In production, use configured backend URL
          const backendUrl = import.meta.env.VITE_BACKEND_URL || 'ws://localhost:8000'
          url = `${backendUrl}/api/v1/ws/events`
          console.log('Using backend URL:', url)
        }
        
        wsEvents.current = new WebSocket(url)
        
        wsEvents.current.onopen = () => {
          if (isMounted.current && !isCleaningUp.current) {
            console.log('Events WebSocket connected')
            retryCount.current.events = 0 // Reset retry count on success
            eventsConnected = true
            // Connection status is primarily based on metrics, events is optional
            setError(null)
          }
        }
        
        wsEvents.current.onmessage = (event) => {
          if (!isMounted.current || isCleaningUp.current) return
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'event' && callbacksRef.current.onEvent) {
              callbacksRef.current.onEvent(data.data)
            }
          } catch (e) {
            console.error('Error parsing event:', e)
          }
        }
        
        wsEvents.current.onerror = (error) => {
          // Suppress errors during cleanup or if not mounted
          if (!isMounted.current || isCleaningUp.current) return
          // Don't log here - let onclose handle it
        }
        
        wsEvents.current.onclose = (event) => {
          // Suppress logs during cleanup
          if (!isMounted.current || isCleaningUp.current) return
          
          eventsConnected = false
          setConnected(false)
          
          // Only retry if it wasn't a normal closure and we haven't exceeded max retries
          if (event.code !== 1000 && event.code !== 1001) {
            const maxRetries = 5
            if (retryCount.current.events < maxRetries) {
              retryCount.current.events++
              const delay = Math.min(1000 * Math.pow(2, retryCount.current.events - 1), 10000) // Exponential backoff, max 10s
              
              console.log(`Events WebSocket disconnected (${event.code}). Retrying in ${delay}ms... (${retryCount.current.events}/${maxRetries})`)
              
              retryTimeouts.current.events = setTimeout(() => {
                if (isMounted.current && !isCleaningUp.current) {
                  connectEvents(true)
                }
              }, delay)
            } else {
              // Already using direct connection, so connection failed
              console.error('Events WebSocket: Max retries reached. Connection failed.')
            }
          } else if (event.code === 1000) {
            console.log('Events WebSocket closed normally')
          }
        }
      } catch (e) {
        if (isMounted.current && !isCleaningUp.current) {
          console.error('Error creating events WebSocket:', e)
        }
      }
    }

    // Use requestAnimationFrame to delay WebSocket creation
    // This gives React StrictMode time to finish its double-mount cycle
    // and prevents errors when cleanup is called before connection is established
    const animationFrameId = requestAnimationFrame(() => {
      // Double-check after animation frame
      if (!isMounted.current || isCleaningUp.current) return
      
      metricsTimeoutId = setTimeout(() => {
        if (isMounted.current && !isCleaningUp.current) {
          connectMetrics()
        }
      }, 10) // Small delay to ensure cleanup has been called if needed

      eventsTimeoutId = setTimeout(() => {
        if (isMounted.current && !isCleaningUp.current) {
          connectEvents()
        }
      }, 10)
    })
    
    // Cleanup function
    return () => {
      isCleaningUp.current = true
      isMounted.current = false
      
      // Cancel requestAnimationFrame if it hasn't fired yet
      cancelAnimationFrame(animationFrameId)
      
      // Clear any pending timeouts
      if (metricsTimeoutId) clearTimeout(metricsTimeoutId)
      if (eventsTimeoutId) clearTimeout(eventsTimeoutId)
      
      // Clear retry timeouts
      if (retryTimeouts.current.metrics) {
        clearTimeout(retryTimeouts.current.metrics)
        retryTimeouts.current.metrics = null
      }
      if (retryTimeouts.current.events) {
        clearTimeout(retryTimeouts.current.events)
        retryTimeouts.current.events = null
      }
      
      // Safely close WebSockets
      safeClose(wsMetrics.current, 'Metrics')
      safeClose(wsEvents.current, 'Events')
      wsMetrics.current = null
      wsEvents.current = null
    }
  }, []) // Empty dependency array - only run on mount/unmount

  return { connected, error }
}
