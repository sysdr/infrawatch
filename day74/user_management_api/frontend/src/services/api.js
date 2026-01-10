import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor for logging (development only)
if (process.env.NODE_ENV === 'development') {
  api.interceptors.request.use(
    (config) => {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });
      return config;
    },
    (error) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor for logging (development only)
  api.interceptors.response.use(
    (response) => {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
      return response;
    },
    (error) => {
      console.error('[API Response Error]', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
      return Promise.reject(error);
    }
  );
}

export const userAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.patch(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  search: (params) => api.get('/search/users', { params }),
};

export const teamAPI = {
  getAll: () => api.get('/teams'),
  getById: (id) => api.get(`/teams/${id}`),
  create: (data) => api.post('/teams', data),
  getMembers: (id) => api.get(`/teams/${id}/members`),
  addMember: (id, data) => api.post(`/teams/${id}/members`, data),
  removeMember: (teamId, userId) => api.delete(`/teams/${teamId}/members/${userId}`),
};

export const permissionAPI = {
  getAll: () => api.get('/permissions'),
  create: (data) => api.post('/permissions', data),
  assignToUser: (userId, data) => api.post(`/permissions/users/${userId}/assign`, data),
  checkPermission: (userId, data) => api.post(`/permissions/users/${userId}/check`, data),
  getUserPermissions: (userId) => api.get(`/permissions/users/${userId}`),
};

export const activityAPI = {
  getUserActivities: (userId, params) => api.get(`/activity/users/${userId}`, { params }),
  getRecent: (params) => api.get('/activity/recent', { params }),
  create: (userId, data) => api.post(`/activity/users/${userId}`, data),
};

export const statsAPI = {
  getStats: () => api.get('/stats'),
};

export default api;
