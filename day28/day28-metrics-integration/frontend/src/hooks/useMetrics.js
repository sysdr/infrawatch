import { useState, useEffect, useCallback, useRef } from 'react';
import ApiService from '../services/api';

export const useMetrics = () => {
  const [metrics, setMetrics] = useState([]);
  const [realtimeMetrics, setRealtimeMetrics] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connected, setConnected] = useState(false);
  
  const eventSourceRef = useRef(null);

  // Query historical metrics
  const queryMetrics = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await ApiService.queryMetrics(params);
      setMetrics(data);
    } catch (err) {
      setError(`Failed to fetch metrics: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  // Get realtime metrics
  const fetchRealtimeMetrics = useCallback(async () => {
    try {
      const data = await ApiService.getRealtimeMetrics();
      setRealtimeMetrics(data.metrics || {});
    } catch (err) {
      console.error('Failed to fetch realtime metrics:', err);
    }
  }, []);

  // Create metric
  const createMetric = useCallback(async (metric) => {
    try {
      const data = await ApiService.createMetric(metric);
      // Refresh metrics after creation
      await queryMetrics();
      return data;
    } catch (err) {
      setError(`Failed to create metric: ${err.message}`);
      throw err;
    }
  }, [queryMetrics]);

  // Setup SSE connection
  useEffect(() => {
    const handleSSEMessage = (data) => {
      if (data.type === 'connected') {
        setConnected(true);
        return;
      }

      if (data.key && data.value) {
        setRealtimeMetrics(prev => ({
          ...prev,
          [data.key]: data.value
        }));
      }
    };

    const handleSSEError = (error) => {
      setConnected(false);
      console.error('SSE Connection Error:', error);
    };

    // Create SSE connection
    eventSourceRef.current = ApiService.createSSEConnection(
      handleSSEMessage,
      handleSSEError
    );

    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Initial data fetch
  useEffect(() => {
    queryMetrics();
    fetchRealtimeMetrics();
  }, [queryMetrics, fetchRealtimeMetrics]);

  return {
    metrics,
    realtimeMetrics,
    loading,
    error,
    connected,
    queryMetrics,
    createMetric,
    fetchRealtimeMetrics
  };
};

export const useHealthCheck = () => {
  const [health, setHealth] = useState(null);
  const [checking, setChecking] = useState(false);

  const checkHealth = useCallback(async () => {
    setChecking(true);
    try {
      const data = await ApiService.healthCheck();
      setHealth(data);
    } catch (err) {
      setHealth({
        status: 'error',
        database: false,
        redis: false,
        timestamp: new Date().toISOString()
      });
    } finally {
      setChecking(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [checkHealth]);

  return { health, checking, checkHealth };
};
