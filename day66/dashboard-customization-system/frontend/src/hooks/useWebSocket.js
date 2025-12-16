import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';

export const useWebSocket = (dashboardId, userId) => {
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [activeUsers, setActiveUsers] = useState([]);

  useEffect(() => {
    if (!dashboardId || !userId) return;

    socketRef.current = io(process.env.REACT_APP_WS_URL);

    socketRef.current.on('connect', () => {
      setConnected(true);
      socketRef.current.emit('join_dashboard', { dashboard_id: dashboardId, user_id: userId });
    });

    socketRef.current.on('disconnect', () => {
      setConnected(false);
    });

    socketRef.current.on('user_joined', (data) => {
      setActiveUsers(data.active_users);
    });

    socketRef.current.on('user_left', (data) => {
      setActiveUsers(prev => prev.filter(id => id !== data.user_id));
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.emit('leave_dashboard', { dashboard_id: dashboardId, user_id: userId });
        socketRef.current.disconnect();
      }
    };
  }, [dashboardId, userId]);

  const emitWidgetUpdate = (widgetData) => {
    if (socketRef.current && connected) {
      socketRef.current.emit('widget_update', { dashboard_id: dashboardId, ...widgetData });
    }
  };

  const emitThemeChange = (theme) => {
    if (socketRef.current && connected) {
      socketRef.current.emit('theme_change', { dashboard_id: dashboardId, theme });
    }
  };

  return { connected, activeUsers, emitWidgetUpdate, emitThemeChange, socket: socketRef.current };
};
