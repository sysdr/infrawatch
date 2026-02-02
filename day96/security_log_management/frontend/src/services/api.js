import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const securityApi = {
  getEvents: (params) => api.get('/security/events', { params }),
  getEvent: (eventId) => api.get(`/security/events/${eventId}`),
  logEvent: (event) => api.post('/security/events', event),
  getStats: () => api.get('/security/stats'),
};

export const auditApi = {
  getTrail: (params) => api.get('/audit/trail', { params }),
  verifyIntegrity: (params) => api.get('/audit/verify', { params }),
  getUserHistory: (userId, days) => api.get(`/audit/user/${userId}`, { params: { days } }),
};

export const incidentApi = {
  getIncidents: (params) => api.get('/incidents/', { params }),
  getIncident: (incidentId) => api.get(`/incidents/${incidentId}`),
  updateIncident: (incidentId, data) => api.patch(`/incidents/${incidentId}`, data),
  getTimeline: (incidentId) => api.get(`/incidents/${incidentId}/timeline`),
};

export const complianceApi = {
  getGDPRReport: (days) => api.get('/compliance/reports/gdpr', { params: { days } }),
  getSOC2Report: (days) => api.get('/compliance/reports/soc2', { params: { days } }),
  verifyIntegrity: () => api.get('/compliance/verify/integrity'),
  getMetrics: () => api.get('/compliance/metrics'),
};

export default api;
