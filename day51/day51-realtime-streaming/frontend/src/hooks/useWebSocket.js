import { useState, useEffect, useCallback, useRef } from 'react'
import { io } from 'socket.io-client'
import pako from 'pako'

export function useWebSocket(url) {
  const [connected, setConnected] = useState(false)
  const [metrics, setMetrics] = useState([])
  const [alerts, setAlerts] = useState([])
  const [stats, setStats] = useState({})
  const socketRef = useRef(null)
  const reconnectAttemptsRef = useRef(0)

  useEffect(() => {
    // Initialize Socket.IO connection
    const socket = io(url, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: Infinity
    })

    socketRef.current = socket

    // Connection handlers
    socket.on('connect', () => {
      console.log('Connected to streaming server')
      setConnected(true)
      reconnectAttemptsRef.current = 0
    })

    socket.on('disconnect', () => {
      console.log('Disconnected from streaming server')
      setConnected(false)
    })

    socket.on('connection_established', (data) => {
      console.log('Connection established:', data)
    })

    // Metrics handler
    socket.on('metrics_update', (data) => {
      setMetrics(prev => {
        const newMetrics = [...prev, data].slice(-60) // Keep last 60 seconds
        return newMetrics
      })
    })

    // Batch metrics handler
    socket.on('metrics_update_batch', (data) => {
      setMetrics(prev => {
        const combined = [...prev, ...data.items].slice(-60)
        return combined
      })
    })

    // Alert handlers
    socket.on('alerts_critical', (alert) => {
      console.log('Received critical alert:', alert)
      setAlerts(prev => [alert, ...prev].slice(0, 20)) // Keep last 20
    })

    socket.on('alerts_warning', (alert) => {
      console.log('Received warning alert:', alert)
      setAlerts(prev => [alert, ...prev].slice(0, 20))
    })

    // Compressed message handler
    socket.on('compressed_message', (data) => {
      try {
        const compressed = new Uint8Array(
          data.data.match(/.{1,2}/g).map(byte => parseInt(byte, 16))
        )
        const decompressed = pako.ungzip(compressed, { to: 'string' })
        const parsed = JSON.parse(decompressed)
        
        if (data.topic === 'metrics_update') {
          setMetrics(prev => [...prev, parsed].slice(-60))
        }
      } catch (error) {
        console.error('Decompression error:', error)
      }
    })

    // Heartbeat
    socket.on('pong', () => {
      // Connection is alive
    })

    const pingInterval = setInterval(() => {
      if (socket.connected) {
        socket.emit('ping')
      }
    }, 30000)

    return () => {
      clearInterval(pingInterval)
      socket.close()
    }
  }, [url])

  const subscribe = useCallback((topics) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('subscribe', { topics })
    }
  }, [])

  const unsubscribe = useCallback((topics) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('unsubscribe', { topics })
    }
  }, [])

  // Fetch stats periodically
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${url}/api/metrics/stats`)
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    }

    if (connected) {
      fetchStats()
      const interval = setInterval(fetchStats, 5000)
      return () => clearInterval(interval)
    }
  }, [connected, url])

  return {
    connected,
    metrics,
    alerts,
    stats,
    subscribe,
    unsubscribe
  }
}
