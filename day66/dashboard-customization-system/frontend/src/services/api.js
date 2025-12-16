import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Clear invalid token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const dashboardApi = {
  create: (data) => api.post('/api/dashboards', data),
  get: (id) => api.get(`/api/dashboards/${id}`),
  update: (id, data) => api.put(`/api/dashboards/${id}`, data),
  list: (isTemplate = false) => api.get('/api/dashboards', { params: { is_template: isTemplate } }),
  listTemplates: () => api.get('/api/dashboards/templates/list'),
  createShare: (id, data) => api.post(`/api/dashboards/${id}/share`, data),
  listShares: (id) => api.get(`/api/dashboards/${id}/shares`),
  revokeShare: (shareId) => api.delete(`/api/dashboards/shares/${shareId}`),
  getShared: (token) => api.get(`/api/dashboards/shared/${token}`)
};

export default api;
