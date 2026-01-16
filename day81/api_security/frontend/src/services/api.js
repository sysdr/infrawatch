import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const apiKeyService = {
  createKey: (data) => api.post('/admin/api-keys', data),
  listKeys: (skip = 0, limit = 100) => api.get(`/admin/api-keys?skip=${skip}&limit=${limit}`),
  revokeKey: (keyId) => api.delete(`/admin/api-keys/${keyId}`),
  rotateKey: (keyId) => api.post(`/admin/api-keys/${keyId}/rotate`)
};

export const requestLogService = {
  getLogs: (skip = 0, limit = 100, apiKeyId = null) => {
    const params = new URLSearchParams({ skip, limit });
    if (apiKeyId) params.append('api_key_id', apiKeyId);
    return api.get(`/admin/request-logs?${params}`);
  }
};

export const analyticsService = {
  getRateLimitStats: (hours = 24) => api.get(`/admin/analytics/rate-limits?hours=${hours}`)
};

export default api;
