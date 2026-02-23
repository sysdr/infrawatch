import { useState, useEffect, useCallback } from 'react';
import { fetchSummary, fetchTimeseries } from '../utils/api';

export function useSummary(hours = 24, refreshMs = 15000) {
  const [data, setData]   = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const result = await fetchSummary(hours);
      setData(result);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [hours]);

  useEffect(() => {
    load();
    const id = setInterval(load, refreshMs);
    return () => clearInterval(id);
  }, [load, refreshMs]);

  return { data, error, loading, refresh: load };
}

export function useTimeseries(metric, hours = 6) {
  const [data, setData]   = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchTimeseries(metric, hours).then(r => {
      setData(r.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [metric, hours]);

  return { data, loading };
}
