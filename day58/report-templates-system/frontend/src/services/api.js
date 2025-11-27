import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const templateApi = {
  getAll: () => api.get('/templates'),
  getById: (id) => api.get(`/templates/${id}`),
  create: (data) => api.post('/templates', data),
  update: (id, data) => api.put(`/templates/${id}`, data),
  delete: (id) => api.delete(`/templates/${id}`),
  preview: (id, data) => api.post(`/templates/${id}/preview`, { data })
};

export const reportApi = {
  getSchedules: () => api.get('/reports/schedules'),
  createSchedule: (data) => api.post('/reports/schedules', data),
  generate: (data) => api.post('/reports/generate', data),
  getExecutions: (scheduledReportId) => {
    const params = scheduledReportId ? { scheduled_report_id: scheduledReportId } : {};
    return api.get('/reports/executions', { params });
  },
  download: (executionId) => 
    api.get(`/reports/executions/${executionId}/download`, { responseType: 'blob' })
};

export default api;
