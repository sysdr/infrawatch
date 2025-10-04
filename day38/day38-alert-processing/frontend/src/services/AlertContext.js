import React, { createContext, useContext, useReducer, useEffect } from 'react';
import AlertService from './AlertService';

const AlertContext = createContext();

const initialState = {
  alerts: [],
  stats: {
    states: {},
    severities: {},
    recent_24h: 0
  },
  loading: false,
  error: null,
  selectedAlert: null
};

function alertReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_ALERTS':
      return { ...state, alerts: action.payload, loading: false };
    case 'ADD_ALERT':
      return { ...state, alerts: [action.payload, ...state.alerts] };
    case 'UPDATE_ALERT':
      return {
        ...state,
        alerts: state.alerts.map(alert =>
          alert.id === action.payload.id ? action.payload : alert
        )
      };
    case 'SET_STATS':
      return { ...state, stats: action.payload };
    case 'SET_SELECTED_ALERT':
      return { ...state, selectedAlert: action.payload };
    default:
      return state;
  }
}

export function AlertProvider({ children }) {
  const [state, dispatch] = useReducer(alertReducer, initialState);

  useEffect(() => {
    // Load initial data
    loadAlerts();
    loadStats();

    // Set up WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'alert_update') {
        dispatch({ type: 'UPDATE_ALERT', payload: data.data });
        // Refresh stats when alerts change
        loadStats();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  const loadAlerts = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const alerts = await AlertService.getAlerts();
      dispatch({ type: 'SET_ALERTS', payload: alerts });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const loadStats = async () => {
    try {
      const stats = await AlertService.getStats();
      dispatch({ type: 'SET_STATS', payload: stats });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const acknowledgeAlert = async (alertId, acknowledgedBy) => {
    try {
      const updatedAlert = await AlertService.acknowledgeAlert(alertId, acknowledgedBy);
      dispatch({ type: 'UPDATE_ALERT', payload: updatedAlert.alert });
      loadStats();
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const resolveAlert = async (alertId, resolvedBy) => {
    try {
      const updatedAlert = await AlertService.resolveAlert(alertId, resolvedBy);
      dispatch({ type: 'UPDATE_ALERT', payload: updatedAlert.alert });
      loadStats();
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const createTestAlert = async () => {
    try {
      const testAlert = {
        title: `Test Alert - ${new Date().toLocaleTimeString()}`,
        description: 'This is a test alert for demonstration',
        metric_name: 'cpu_usage',
        service_name: 'web-server',
        current_value: Math.random() * 100,
        threshold_value: 80
      };
      
      const result = await AlertService.createAlert(testAlert);
      dispatch({ type: 'ADD_ALERT', payload: result.alert });
      loadStats();
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const value = {
    ...state,
    loadAlerts,
    loadStats,
    acknowledgeAlert,
    resolveAlert,
    createTestAlert,
    setSelectedAlert: (alert) => dispatch({ type: 'SET_SELECTED_ALERT', payload: alert })
  };

  return (
    <AlertContext.Provider value={value}>
      {children}
    </AlertContext.Provider>
  );
}

export function useAlerts() {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error('useAlerts must be used within AlertProvider');
  }
  return context;
}
