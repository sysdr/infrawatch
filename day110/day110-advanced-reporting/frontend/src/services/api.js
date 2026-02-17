import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const reportAPI = {
  listReports: () => api.get('/reports'),
  createReport: (data) => api.post('/reports', data),
  generateReport: (reportId) => api.post(`/reports/${reportId}/generate`),
  getExecutions: (reportId) => api.get(`/reports/${reportId}/executions`),
};

export const templateAPI = {
  listTemplates: () => api.get('/templates'),
  createTemplate: (data) => api.post('/templates', data),
  getTemplate: (id) => api.get(`/templates/${id}`),
  updateTemplate: (id, data) => api.put(`/templates/${id}`, data),
};

export const scheduleAPI = {
  listSchedules: () => api.get('/schedules'),
  createSchedule: (data) => api.post('/schedules', data),
  deleteSchedule: (id) => api.delete(`/schedules/${id}`),
};

export const distributionAPI = {
  listDistributionLists: () => api.get('/distribution/lists'),
  createDistributionList: (data) => api.post('/distribution/lists', data),
  distributeReport: (executionId, listId) => api.post(`/distribution/send/${executionId}/${listId}`),
};

export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
};

export default api;
