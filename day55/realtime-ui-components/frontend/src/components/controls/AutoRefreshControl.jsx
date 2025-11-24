import React, { useEffect, useRef } from 'react';
import { RefreshCw, Pause } from 'lucide-react';
import axios from 'axios';
import { useRealtime } from '../../contexts/RealtimeContext';

function AutoRefreshControl({ enabled, onToggle }) {
  const { connectionStatus } = useRealtime();
  const intervalRef = useRef(null);

  useEffect(() => {
    if (enabled && connectionStatus === 'offline') {
      // Use polling when WebSocket is offline
      intervalRef.current = setInterval(async () => {
        try {
          const response = await axios.get('/api/stats');
          console.log('Polled stats:', response.data);
        } catch (error) {
          console.error('Polling failed:', error);
        }
      }, 5000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, connectionStatus]);

  return (
    <button 
      className={`refresh-control ${enabled ? 'active' : ''}`}
      onClick={() => onToggle(!enabled)}
      title={enabled ? 'Disable auto-refresh' : 'Enable auto-refresh'}
    >
      {enabled ? <RefreshCw size={18} className="spinning" /> : <Pause size={18} />}
      <span>{enabled ? 'Auto-refresh ON' : 'Auto-refresh OFF'}</span>
    </button>
  );
}

export default AutoRefreshControl;
