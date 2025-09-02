import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { metricsWebSocket } from '../services/websocket';

export const useMetrics = (metricName, timeRange = '1h') => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistoricalData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const endTime = new Date();
      const startTime = new Date();
      
      // Calculate start time based on range
      switch (timeRange) {
        case '1h':
          startTime.setHours(startTime.getHours() - 1);
          break;
        case '24h':
          startTime.setDate(startTime.getDate() - 1);
          break;
        case '7d':
          startTime.setDate(startTime.getDate() - 7);
          break;
        case '30d':
          startTime.setDate(startTime.getDate() - 30);
          break;
        default:
          startTime.setHours(startTime.getHours() - 1);
      }

      const metrics = await apiService.getMetrics({
        metric_name: metricName,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        limit: 1000
      });

      setData(metrics.reverse()); // Reverse to get chronological order
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [metricName, timeRange]);

  const handleRealtimeUpdate = useCallback((update) => {
    setData(prevData => {
      const newData = [...prevData, {
        ...update,
        timestamp: update.timestamp
      }];
      
      // Keep only last 1000 points for performance
      return newData.slice(-1000);
    });
  }, []);

  useEffect(() => {
    if (!metricName) return;

    fetchHistoricalData();
    
    // Connect WebSocket if not already connected
    if (!metricsWebSocket.socket || metricsWebSocket.socket.readyState !== WebSocket.OPEN) {
      metricsWebSocket.connect();
    }

    // Subscribe to real-time updates
    metricsWebSocket.subscribe(metricName, handleRealtimeUpdate);

    return () => {
      metricsWebSocket.unsubscribe(metricName, handleRealtimeUpdate);
    };
  }, [metricName, timeRange, fetchHistoricalData, handleRealtimeUpdate]);

  return { data, loading, error, refetch: fetchHistoricalData };
};

export const useMetricNames = () => {
  const [names, setNames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNames = async () => {
      try {
        const metricNames = await apiService.getMetricNames();
        setNames(metricNames);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchNames();
  }, []);

  return { names, loading, error };
};
