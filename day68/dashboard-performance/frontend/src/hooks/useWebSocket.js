import { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

export const useWebSocket = (url) => {
  const [connected, setConnected] = useState(false);
  const [metrics, setMetrics] = useState({});
  const socketRef = useRef(null);
  const updateQueueRef = useRef(new Map());

  useEffect(() => {
    // Extract base URL from ws:// or http:// URL
    // Socket.IO client expects http:// or https://, not ws://
    const baseUrl = url.replace(/^ws:\/\//, 'http://').replace(/\/ws\/metrics.*$/, '');
    console.log('Connecting to Socket.IO at:', baseUrl, 'with path:', '/ws/metrics');
    socketRef.current = io(baseUrl, {
      transports: ['websocket'],
      path: '/ws/metrics',
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    socketRef.current.on('connect', () => {
      console.log('Socket.IO connected');
      setConnected(true);
    });

    socketRef.current.on('disconnect', (reason) => {
      console.log('Socket.IO disconnected:', reason);
      setConnected(false);
    });

    socketRef.current.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error);
      setConnected(false);
    });

    socketRef.current.on('error', (error) => {
      console.error('Socket.IO error:', error);
    });

    socketRef.current.on('message', (data) => {
      // Socket.IO already parses JSON, so data is already an object
      const message = typeof data === 'string' ? JSON.parse(data) : data;
      
      if (message.type === 'metrics_update') {
        // Queue updates instead of applying immediately
        message.data.forEach(update => {
          updateQueueRef.current.set(update.metric_id, update);
        });
      }
    });

    // Batch update application using RAF
    let rafId;
    const flushUpdates = () => {
      if (updateQueueRef.current.size > 0) {
        const updates = Object.fromEntries(updateQueueRef.current);
        updateQueueRef.current.clear();
        
        setMetrics(prev => ({
          ...prev,
          ...updates
        }));
      }
      
      rafId = requestAnimationFrame(flushUpdates);
    };
    
    rafId = requestAnimationFrame(flushUpdates);

    return () => {
      cancelAnimationFrame(rafId);
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [url]);

  return { connected, metrics };
};
