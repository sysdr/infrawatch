import { useEffect, useRef } from 'react';
import useAnalyticsStore from '../store/analyticsStore';

const WS_URL = (process.env.REACT_APP_WS_URL || 'ws://localhost:8000').replace('http', 'ws');

export function useWebSocket() {
  const { setKpis, setDashboardState } = useAnalyticsStore();
  const wsRef = useRef(null);

  useEffect(() => {
    function connect() {
      const ws = new WebSocket(`${WS_URL}/api/v1/analytics/ws`);
      wsRef.current = ws;

      ws.onopen = () => setDashboardState('READY');
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === 'dashboard_update') {
            setKpis(msg.data.kpis, msg.data.updated_at);
          }
        } catch (_) {}
      };
      ws.onclose = () => {
        setDashboardState('REFRESHING');
        setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
    }

    connect();
    return () => { wsRef.current?.close(); };
  }, [setKpis, setDashboardState]);
}
