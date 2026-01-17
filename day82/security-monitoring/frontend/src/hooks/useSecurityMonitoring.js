import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function useSecurityMonitoring() {
  const [summary, setSummary] = useState(null);
  const [threats, setThreats] = useState([]);
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch summary
        const summaryRes = await axios.get(`${API_URL}/api/analytics/summary`);
        setSummary(summaryRes.data);
        
        // Fetch active threats
        const threatsRes = await axios.get(`${API_URL}/api/threats/active`);
        setThreats(threatsRes.data);
        
        // Fetch recent events
        const eventsRes = await axios.get(`${API_URL}/api/events/recent?limit=50`);
        setEvents(eventsRes.data);
        
        setIsConnected(true);
        setError(null);
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return {
    summary,
    threats,
    events,
    isConnected,
    loading,
    error
  };
}
