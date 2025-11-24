import React, { createContext, useContext, useEffect, useReducer, useCallback, useRef } from 'react';

const RealtimeContext = createContext();

const initialState = {
  connectionStatus: 'connecting',
  latency: 0,
  lastUpdate: null,
  userCount: 0,
  messageRate: 0,
  offlineQueue: [],
  data: {}
};

function realtimeReducer(state, action) {
  switch (action.type) {
    case 'SET_CONNECTION_STATUS':
      return { ...state, connectionStatus: action.payload };
    case 'SET_LATENCY':
      return { ...state, latency: action.payload };
    case 'SET_LAST_UPDATE':
      return { ...state, lastUpdate: action.payload };
    case 'UPDATE_DATA':
      return {
        ...state,
        data: { ...state.data, ...action.payload },
        lastUpdate: new Date().toISOString()
      };
    case 'SET_USER_COUNT':
      return { ...state, userCount: action.payload };
    case 'SET_MESSAGE_RATE':
      return { ...state, messageRate: action.payload };
    case 'ADD_TO_QUEUE':
      return {
        ...state,
        offlineQueue: [...state.offlineQueue, action.payload]
      };
    case 'CLEAR_QUEUE':
      return { ...state, offlineQueue: [] };
    default:
      return state;
  }
}

export function RealtimeProvider({ children }) {
  const [state, dispatch] = useReducer(realtimeReducer, initialState);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const pingIntervalRef = useRef(null);
  const offlineQueueRef = useRef([]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connecting' });

    // Use proxy path for WebSocket connection (Vite will proxy to backend)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connected' });
      reconnectAttempts.current = 0;

      // Start ping interval
      pingIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          const start = Date.now();
          ws.send(JSON.stringify({
            type: 'ping',
            data: { client_timestamp: start }
          }));
        }
      }, 5000);

      // Process offline queue
      if (offlineQueueRef.current.length > 0) {
        offlineQueueRef.current.forEach(msg => {
          ws.send(JSON.stringify(msg));
        });
        offlineQueueRef.current = [];
        dispatch({ type: 'CLEAR_QUEUE' });
      }
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'pong') {
        const latency = Date.now() - message.data.latency;
        dispatch({ type: 'SET_LATENCY', payload: latency });
      } else if (message.type === 'user_count') {
        dispatch({ type: 'SET_USER_COUNT', payload: message.data.count });
      } else if (message.type === 'message_rate') {
        dispatch({ type: 'SET_MESSAGE_RATE', payload: message.data.rate });
      } else if (message.type === 'metrics') {
        dispatch({ type: 'UPDATE_DATA', payload: message.data });
      }

      dispatch({ type: 'SET_LAST_UPDATE', payload: new Date().toISOString() });
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      // Don't set status here, let onclose handle it
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed', event.code, event.reason);
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }

      // Only reconnect if not intentionally closed (code 1000 = normal closure)
      // Also check if wsRef still points to this connection
      if (event.code !== 1000 && wsRef.current === ws) {
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'reconnecting' });

        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current++;

        if (reconnectAttempts.current > 5) {
          dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'offline' });
        } else {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      } else if (event.code === 1000) {
        // Normal closure, set status to offline
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'offline' });
      }
    };
  }, []);

  useEffect(() => {
    // Small delay to ensure backend is ready
    const connectTimeout = setTimeout(() => {
      connect();
    }, 100);

    return () => {
      clearTimeout(connectTimeout);
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // Queue for later
      offlineQueueRef.current.push(message);
      dispatch({ type: 'ADD_TO_QUEUE', payload: message });
    }
  }, []);

  const value = {
    ...state,
    sendMessage,
    reconnect: connect
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
}

export function useRealtime() {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within RealtimeProvider');
  }
  return context;
}
