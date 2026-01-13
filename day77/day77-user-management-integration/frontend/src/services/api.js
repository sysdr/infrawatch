import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const userAPI = {
  getAll: () => api.get('/users'),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  activate: (id) => api.post(`/users/${id}/activate`),
  suspend: (id) => api.post(`/users/${id}/suspend`),
  archive: (id) => api.post(`/users/${id}/archive`),
};

export const teamAPI = {
  getAll: () => api.get('/teams'),
  getById: (id) => api.get(`/teams/${id}`),
  create: (data) => api.post('/teams', data),
  addMember: (teamId, data) => api.post(`/teams/${teamId}/members`, data),
  removeMember: (teamId, userId) => api.delete(`/teams/${teamId}/members/${userId}`),
};

export const permissionAPI = {
  grantUser: (data) => api.post('/permissions/users', data),
  grantTeam: (data) => api.post('/permissions/teams', data),
  getUserPermissions: (userId) => api.get(`/permissions/users/${userId}`),
  check: (data) => api.post('/permissions/check', data),
};

export const testAPI = {
  runTests: () => api.post('/tests/run-integration-tests'),
  getResults: (testId) => api.get(`/tests/results/${testId}`),
  getStatus: () => api.get('/tests/status'),
};

export default api;
