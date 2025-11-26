import { useState, useEffect, useCallback, useRef } from 'react';

export const useWebSocket = (url) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('DISCONNECTED');
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const urlRef = useRef(url);
  const isUnmountingRef = useRef(false);

  // Update URL ref when it changes
  useEffect(() => {
    urlRef.current = url;
  }, [url]);

  const connect = useCallback(() => {
    // Don't connect if unmounting
    if (isUnmountingRef.current) {
      return;
    }

    // Don't create new connection if one already exists and is connecting/open
    if (wsRef.current) {
      const state = wsRef.current.readyState;
      if (state === WebSocket.CONNECTING || state === WebSocket.OPEN) {
        return;
      }
      // Close existing connection if it's closing or closed
      if (state === WebSocket.CLOSING || state === WebSocket.CLOSED) {
        try {
          wsRef.current.onclose = null;
          wsRef.current.onerror = null;
          wsRef.current.onopen = null;
          wsRef.current.onmessage = null;
        } catch (e) {
          // Ignore
        }
        wsRef.current = null;
      }
    }
    
    try {
      const ws = new WebSocket(urlRef.current);
      
      ws.onopen = () => {
        if (isUnmountingRef.current) {
          ws.close();
          return;
        }
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionState('CONNECTED');
        reconnectAttemptRef.current = 0;
      };

      ws.onmessage = (event) => {
        if (isUnmountingRef.current) {
          return;
        }
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = (error) => {
        if (!isUnmountingRef.current) {
          console.error('WebSocket error:', error);
          setConnectionState('ERROR');
        }
      };

      ws.onclose = (event) => {
        if (isUnmountingRef.current) {
          return;
        }
        console.log('WebSocket disconnected', event.code, event.reason);
        setIsConnected(false);
        setConnectionState('DISCONNECTED');
        
        // Only reconnect if not a normal closure and attempts < 10
        if (event.code !== 1000 && reconnectAttemptRef.current < 10 && !isUnmountingRef.current) {
          const delay = Math.min(
            30000,
            1000 * Math.pow(2, reconnectAttemptRef.current)
          ) + Math.random() * 1000;
          
          reconnectAttemptRef.current += 1;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (reconnectAttemptRef.current <= 10 && !isUnmountingRef.current) {
              setConnectionState('RECONNECTING');
              connect();
            }
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      if (!isUnmountingRef.current) {
        console.error('Failed to connect:', error);
        setConnectionState('ERROR');
      }
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }, []);

  useEffect(() => {
    isUnmountingRef.current = false;
    connect();

    return () => {
      isUnmountingRef.current = true;
      
      // Clear reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      
      // Close WebSocket connection
      if (wsRef.current) {
        try {
          // Remove all handlers to prevent callbacks during cleanup
          wsRef.current.onclose = null;
          wsRef.current.onerror = null;
          wsRef.current.onopen = null;
          wsRef.current.onmessage = null;
          
          // Close if not already closed
          if (wsRef.current.readyState !== WebSocket.CLOSED && wsRef.current.readyState !== WebSocket.CLOSING) {
            wsRef.current.close(1000, 'Component unmounting');
          }
        } catch (e) {
          // Ignore errors during cleanup
        }
        wsRef.current = null;
      }
    };
  }, []); // Empty deps - only run once on mount

  return {
    isConnected,
    connectionState,
    lastMessage,
    sendMessage
  };
};
