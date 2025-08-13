import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log('API Request:', config.method?.toUpperCase(), config.url);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export interface Server {
  id: number;
  name: string;
  status: 'creating' | 'starting' | 'running' | 'stopping' | 'stopped' | 'error';
  ip_address?: string;
  port?: number;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateServerRequest {
  name: string;
  description?: string;
  ip_address?: string;
  port?: number;
}

export const serverApi = {
  // Get all servers
  getServers: async (): Promise<Server[]> => {
    const response = await api.get('/servers');
    return response.data.data;
  },

  // Get single server
  getServer: async (id: number): Promise<Server> => {
    const response = await api.get(`/servers/${id}`);
    return response.data.data;
  },

  // Create server
  createServer: async (data: CreateServerRequest): Promise<Server> => {
    const response = await api.post('/servers', data);
    return response.data.data;
  },

  // Update server status
  updateServerStatus: async (id: number, status: string): Promise<Server> => {
    const response = await api.put(`/servers/${id}/status?status=${status}`);
    return response.data.data;
  },

  // Delete server
  deleteServer: async (id: number): Promise<void> => {
    await api.delete(`/servers/${id}`);
  },
};

export default api;
