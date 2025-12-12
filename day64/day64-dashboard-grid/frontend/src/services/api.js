import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardAPI = {
  getAll: () => api.get('/dashboards/'),
  getById: (id) => api.get(`/dashboards/${id}`),
  create: (data) => api.post('/dashboards/', data),
  update: (id, data) => api.put(`/dashboards/${id}`, data),
  delete: (id) => api.delete(`/dashboards/${id}`),
};

export const widgetAPI = {
  getByDashboard: (dashboardId) => api.get(`/widgets/dashboard/${dashboardId}`),
  create: (data) => api.post('/widgets/', data),
  update: (id, data) => api.put(`/widgets/${id}`, data),
  delete: (id) => api.delete(`/widgets/${id}`),
};

export const templateAPI = {
  getAll: () => api.get('/templates/'),
  create: (data) => api.post('/templates/', data),
  apply: (templateId, dashboardId) => api.post(`/templates/${templateId}/apply/${dashboardId}`),
};

export default api;
