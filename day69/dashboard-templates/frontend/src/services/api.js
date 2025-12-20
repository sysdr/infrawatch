import axios from 'axios'

const API_BASE = '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const templateApi = {
  search: (params) => api.get('/templates', { params }),
  get: (id) => api.get(`/templates/${id}`),
  create: (data) => api.post('/templates', data),
  update: (id, data) => api.put(`/templates/${id}`, data),
  publish: (id) => api.post(`/templates/${id}/publish`),
  getVersions: (id) => api.get(`/templates/${id}/versions`),
  instantiate: (id, data) => api.post(`/templates/${id}/instantiate`, data),
  rate: (id, data) => api.post(`/templates/${id}/rate`, data)
}

export const dashboardApi = {
  list: () => api.get('/dashboards')
}

export const statsApi = {
  get: () => api.get('/stats'),
  getCategories: () => api.get('/categories')
}

export default api
