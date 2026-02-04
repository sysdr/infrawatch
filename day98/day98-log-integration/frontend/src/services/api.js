import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchLogs = async (params) => {
  const response = await api.get('/api/logs/search', { params });
  return response.data;
};

export const getAlerts = async () => {
  const response = await api.get('/api/alerts');
  return response.data;
};

export const resolveAlert = async (alertId) => {
  const response = await api.post(`/api/alerts/${alertId}/resolve`);
  return response.data;
};

export const getMetrics = async () => {
  const response = await api.get('/metrics');
  return response.data;
};

export default api;
