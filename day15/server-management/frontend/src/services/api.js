import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const serverService = {
  getServers: async (filters = {}) => {
    const params = Object.entries(filters)
      .filter(([key, value]) => value)
      .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {});
    
    const response = await api.get('/api/servers/', { params });
    return response.data;
  },

  getServer: async (id) => {
    const response = await api.get(`/api/servers/${id}`);
    return response.data;
  },

  createServer: async (serverData) => {
    const response = await api.post('/api/servers/', serverData);
    return response.data;
  },

  updateServer: async (id, serverData) => {
    const response = await api.put(`/api/servers/${id}`, serverData);
    return response.data;
  },

  getTags: async () => {
    const response = await api.get('/api/servers/tags/');
    return response.data;
  },

  createTag: async (tagData) => {
    const response = await api.post('/api/servers/tags/', tagData);
    return response.data;
  },

  addHealthCheck: async (serverId, healthData) => {
    const response = await api.post(`/api/servers/${serverId}/health`, healthData);
    return response.data;
  },
};
