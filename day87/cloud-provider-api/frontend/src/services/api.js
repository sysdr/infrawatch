import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const resourcesAPI = {
  getAll: (params) => api.get('/api/v1/resources/', { params }),
  getSummary: () => api.get('/api/v1/resources/summary'),
};

export const costsAPI = {
  getCurrent: () => api.get('/api/v1/costs/current'),
  getSummary: () => api.get('/api/v1/costs/summary'),
  getForecast: (days) => api.get('/api/v1/costs/forecast', { params: { days } }),
};

export const healthAPI = {
  getMetrics: (resourceId) => api.get(`/api/v1/health/metrics/${resourceId}`),
  getSummary: () => api.get('/api/v1/health/summary'),
};

export const autoscalingAPI = {
  getEvents: (hours) => api.get('/api/v1/autoscaling/events', { params: { hours } }),
  getGroups: () => api.get('/api/v1/autoscaling/groups'),
};

export const systemAPI = {
  getStatus: () => api.get('/api/v1/status'),
};

export default api;
