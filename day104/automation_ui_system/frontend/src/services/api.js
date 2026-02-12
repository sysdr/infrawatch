import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const workflowApi = {
  getAll: () => api.get('/workflows'),
  getById: (id) => api.get(`/workflows/${id}`),
  create: (data) => api.post('/workflows', data),
  update: (id, data) => api.put(`/workflows/${id}`, data),
  delete: (id) => api.delete(`/workflows/${id}`),
  execute: (id, data) => api.post(`/workflows/${id}/execute`, data),
  getExecutions: (id) => api.get(`/workflows/${id}/executions`),
};

export const executionApi = {
  getAll: () => api.get('/executions'),
  getById: (id) => api.get(`/executions/${id}`),
  getSteps: (id) => api.get(`/executions/${id}/steps`),
};

export const scriptApi = {
  getAll: () => api.get('/scripts'),
  getById: (id) => api.get(`/scripts/${id}`),
  create: (data) => api.post('/scripts', data),
  update: (id, data) => api.put(`/scripts/${id}`, data),
  delete: (id) => api.delete(`/scripts/${id}`),
};

export const analyticsApi = {
  getOverview: () => api.get('/analytics/overview'),
  getTimeline: (days = 7) => api.get(`/analytics/executions/timeline?days=${days}`),
  getTopWorkflows: (limit = 10) => api.get(`/analytics/workflows/top?limit=${limit}`),
};

export default api;
