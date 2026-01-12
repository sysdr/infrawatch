import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const userAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
}

export const teamAPI = {
  getAll: () => api.get('/teams'),
  create: (data) => api.post('/teams', data),
  addMember: (teamId, userId) => api.post(`/teams/${teamId}/members/${userId}`),
  removeMember: (teamId, userId) => api.delete(`/teams/${teamId}/members/${userId}`),
}

export const roleAPI = {
  getAll: () => api.get('/roles'),
  assign: (userId, roleId) => api.post(`/users/${userId}/roles/${roleId}`),
  revoke: (userId, roleId) => api.delete(`/users/${userId}/roles/${roleId}`),
}

export const activityAPI = {
  getAll: (params) => api.get('/activities', { params }),
}

export default api
