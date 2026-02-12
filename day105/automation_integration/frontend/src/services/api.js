import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const workflowsApi = {
  list: () => api.get('/workflows'),
  get: (id) => api.get(`/workflows/${id}`),
  create: (data) => api.post('/workflows', data),
};

export const executionsApi = {
  list: (status = null) => {
    const params = status ? { status } : {};
    return api.get('/executions', { params });
  },
  get: (id) => api.get(`/executions/${id}`),
  create: (data) => api.post('/executions', data),
  getSteps: (id) => api.get(`/executions/${id}/steps`),
  getLogs: (id) => api.get(`/executions/${id}/logs`),
  retry: (id) => api.post(`/executions/${id}/retry`),
};

export const securityApi = {
  getChecks: (executionId) => api.get(`/security/checks/${executionId}`),
  listViolations: () => api.get('/security/violations'),
  getStats: () => api.get('/security/stats'),
};

export const monitoringApi = {
  getMetrics: () => api.get('/monitoring/metrics'),
  getHealth: () => api.get('/monitoring/health'),
};

export default api;
