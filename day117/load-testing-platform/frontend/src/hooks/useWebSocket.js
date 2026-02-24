import { useEffect, useRef, useState, useCallback } from 'react';

export function useWebSocket(url) {
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!url) return;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        setMessages(prev => [...prev.slice(-300), data]);
      } catch {}
    };

    return () => ws.close();
  }, [url]);

  return { messages, connected };
}
