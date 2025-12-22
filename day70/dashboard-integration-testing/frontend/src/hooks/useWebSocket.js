import { useEffect, useState, useCallback, useRef } from 'react';
import io from 'socket.io-client';

const SOCKET_URL = 'ws://localhost:8000';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState([]);
  const [performanceStats, setPerformanceStats] = useState(null);
  const socketRef = useRef(null);
  const metricsBufferRef = useRef([]);
  const lastFlushRef = useRef(Date.now());

  const flushMetrics = useCallback(() => {
    if (metricsBufferRef.current.length > 0) {
      setMetrics(metricsBufferRef.current);
      metricsBufferRef.current = [];
      lastFlushRef.current = Date.now();
    }
  }, []);

  useEffect(() => {
    const clientId = `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const socket = new WebSocket(`${SOCKET_URL}/ws/dashboard/${clientId}`);

    socket.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
      
      // Send heartbeat every 30 seconds
      const heartbeat = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);

      socketRef.current = { socket, heartbeat };
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'metrics_batch') {
        // Add to buffer for batched rendering
        metricsBufferRef.current.push(...data.data);
        
        // Flush every 1000ms (1 second) for better visibility
        if (Date.now() - lastFlushRef.current > 1000) {
          flushMetrics();
        }
      } else if (data.type === 'metrics_priority') {
        // Priority metrics render immediately
        setMetrics(data.data);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    // Periodic flush to catch any remaining buffered metrics (every 1 second)
    const flushInterval = setInterval(flushMetrics, 1000);

    // Fetch initial performance stats
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/performance/stats');
        const stats = await response.json();
        setPerformanceStats(stats);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };
    fetchStats();
    const statsInterval = setInterval(fetchStats, 5000);

    return () => {
      if (socketRef.current) {
        clearInterval(socketRef.current.heartbeat);
        socketRef.current.socket.close();
      }
      clearInterval(flushInterval);
      clearInterval(statsInterval);
    };
  }, [flushMetrics]);

  const setLoadLevel = useCallback((level) => {
    if (socketRef.current && socketRef.current.socket.readyState === WebSocket.OPEN) {
      socketRef.current.socket.send(JSON.stringify({
        type: 'set_load',
        load: level
      }));
    }
  }, []);

  return {
    isConnected,
    metrics,
    performanceStats,
    setLoadLevel
  };
}
