import React, { createContext, useContext, useEffect, useRef, useState } from 'react';

const WebSocketContext = createContext({ lastMessage: null });

export const WebSocketProvider = ({ children }) => {
  const wsRef = useRef(null);
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    const url = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + (window.location.hostname || 'localhost') + ':8000/ws';
    wsRef.current = new WebSocket(url);
    wsRef.current.onmessage = (event) => setLastMessage(event);
    wsRef.current.onopen = () => wsRef.current?.send(JSON.stringify({ type: 'subscribe', room: 'default' }));
    return () => { try { wsRef.current?.close(); } catch (_) {} };
  }, []);

  return (
    <WebSocketContext.Provider value={{ lastMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => useContext(WebSocketContext);
