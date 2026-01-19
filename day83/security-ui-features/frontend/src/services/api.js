import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const securityApi = {
  // Events
  getEvents: (params) => apiClient.get('/api/security/events/', { params }),
  getEvent: (eventId) => apiClient.get(`/api/security/events/${eventId}`),
  resolveEvent: (eventId, resolvedBy) => 
    apiClient.patch(`/api/security/events/${eventId}/resolve`, null, { params: { resolved_by: resolvedBy } }),
  getEventSummary: () => apiClient.get('/api/security/events/stats/summary'),
  
  // Metrics
  getDashboardMetrics: () => apiClient.get('/api/security/metrics/dashboard'),
  getThreatDistribution: () => apiClient.get('/api/security/metrics/threat-distribution'),
  getTimeline: (hours = 24) => apiClient.get('/api/security/metrics/timeline', { params: { hours } }),
  
  // Settings
  getSettings: (params) => apiClient.get('/api/security/settings/', { params }),
  getSetting: (settingKey) => apiClient.get(`/api/security/settings/${settingKey}`),
  createSetting: (data) => apiClient.post('/api/security/settings/', data),
  updateSetting: (settingKey, data) => apiClient.put(`/api/security/settings/${settingKey}`, data),
  getCategories: () => apiClient.get('/api/security/settings/categories/list'),
  
  // Audit Logs
  getAuditLogs: (params) => apiClient.get('/api/security/audit/', { params }),
  getAuditLog: (logId) => apiClient.get(`/api/security/audit/${logId}`),
  getAuditSummary: () => apiClient.get('/api/security/audit/stats/summary'),
  
  // Reports
  getDailyReport: () => apiClient.get('/api/security/reports/daily'),
  getWeeklyReport: () => apiClient.get('/api/security/reports/weekly'),
  getComplianceReport: () => apiClient.get('/api/security/reports/compliance'),
};

export default apiClient;
