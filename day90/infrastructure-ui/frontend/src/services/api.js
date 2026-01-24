import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const topologyAPI = {
  getTopology: (params) => api.get('/topology', { params }),
};

export const resourcesAPI = {
  listResources: (params) => api.get('/resources', { params }),
  getResource: (id) => api.get(`/resources/${id}`),
  createResource: (data) => api.post('/resources', data),
  updateResource: (id, data) => api.patch(`/resources/${id}`, data),
  deleteResource: (id) => api.delete(`/resources/${id}`),
};

export const costsAPI = {
  getSummary: (days) => api.get('/costs/summary', { params: { days } }),
  getTrends: (days) => api.get('/costs/trends', { params: { days } }),
  getForecast: (days) => api.get('/costs/forecast', { params: { days } }),
  getTopResources: (limit) => api.get('/costs/top-resources', { params: { limit } }),
};

export const reportsAPI = {
  getInventory: () => api.get('/reports/inventory'),
  getUtilization: () => api.get('/reports/utilization'),
  getCompliance: () => api.get('/reports/compliance'),
};

export default api;
