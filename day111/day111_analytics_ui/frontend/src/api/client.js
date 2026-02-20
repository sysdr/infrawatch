import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: `${BASE}/api/v1`, headers: { 'Content-Type': 'application/json' } });

export const analyticsApi = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getMetricSeries: (name, hours = 6) => api.get(`/analytics/metrics/${name}?hours=${hours}`),
  computeCorrelation: (payload) => api.post('/analytics/correlate', payload),
};

export const mlApi = {
  predict: (payload) => api.post('/ml/predict', payload),
  listModels: () => api.get('/ml/models'),
};

export const reportsApi = {
  create: (payload) => api.post('/reports/', payload),
  list: () => api.get('/reports/'),
  exportCsv: (id) => `${BASE}/api/v1/reports/${id}/export/csv`,
  exportPdf: (id) => `${BASE}/api/v1/reports/${id}/export/pdf`,
};

export const configApi = {
  getAll: () => api.get('/config/'),
  update: (key, value) => api.patch('/config/', { key, value }),
};

export default api;
