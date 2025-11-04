import { useState, useEffect, useRef } from 'react'
import toast from 'react-hot-toast'

const useWebSocket = (url, userId = 'demo-user') => {
  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState([])
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttemptsRef = useRef(0)

  const connect = () => {
    try {
      const ws = new WebSocket(url)
      
      ws.onopen = () => {
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
        
        // Subscribe to user notifications
        ws.send(JSON.stringify({
          type: 'subscribe',
          userId: userId
        }))
        
        toast.success('Connected to notification server')
      }
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        setMessages(prev => [...prev, message])
        
        if (message.type === 'notification') {
          const notif = message.data
          const toastOptions = {
            duration: 5000,
            style: {
              background: getNotificationColor(notif.type),
              color: 'white',
            },
          }
          
          toast(
            `${notif.title}: ${notif.message}`,
            toastOptions
          )
        }
      }
      
      ws.onclose = () => {
        setIsConnected(false)
        setSocket(null)
        
        // Attempt to reconnect
        if (reconnectAttemptsRef.current < 5) {
          reconnectAttemptsRef.current += 1
          const delay = Math.pow(2, reconnectAttemptsRef.current) * 1000
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, delay)
          
          toast.error(`Connection lost. Reconnecting in ${delay/1000}s...`)
        } else {
          toast.error('Failed to maintain connection to notification server')
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        toast.error('WebSocket connection error')
      }
      
      setSocket(ws)
      
    } catch (error) {
      console.error('Failed to connect:', error)
      toast.error('Failed to connect to notification server')
    }
  }

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (socket) {
      socket.close()
    }
  }

  const sendMessage = (message) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message))
    }
  }

  const acknowledgeNotification = (notificationId) => {
    sendMessage({
      type: 'acknowledge',
      notificationId: notificationId
    })
  }

  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [url, userId])

  return {
    socket,
    isConnected,
    messages,
    sendMessage,
    acknowledgeNotification,
    connect,
    disconnect
  }
}

const getNotificationColor = (type) => {
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6',
  }
  return colors[type] || colors.info
}

export default useWebSocket
