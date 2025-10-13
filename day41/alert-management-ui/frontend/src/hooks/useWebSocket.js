import { useState, useEffect, useRef } from 'react';

export const useWebSocket = (url) => {
  const [messages, setMessages] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('Connecting');
  const ws = useRef(null);

  useEffect(() => {
    const connectWebSocket = () => {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setConnectionStatus('Connected');
      };

      ws.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        setMessages(prev => [...prev, message]);
      };

      ws.current.onclose = () => {
        setConnectionStatus('Disconnected');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      ws.current.onerror = () => {
        setConnectionStatus('Error');
      };
    };

    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  return { messages, connectionStatus };
};
