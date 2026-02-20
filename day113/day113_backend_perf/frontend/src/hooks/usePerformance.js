import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchPerformance } from '../services/api';

export function usePerformance(pollMs = 3000) {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const load = useCallback(async () => {
    try {
      const d = await fetchPerformance();
      setData(d);
      setHistory(prev => {
        const ts = new Date().toLocaleTimeString();
        const entry = {
          time: ts,
          p50: d.latency.p50_ms,
          p95: d.latency.p95_ms,
          p99: d.latency.p99_ms,
          hitRate: d.cache.hit_rate_pct,
          poolUtil: d.pool.utilisation_pct,
          cpu: d.system.cpu_pct,
        };
        return [...prev, entry].slice(-30);
      });
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    load();
    intervalRef.current = setInterval(load, pollMs);
    return () => clearInterval(intervalRef.current);
  }, [load, pollMs]);

  return { data, history, error, refresh: load };
}
