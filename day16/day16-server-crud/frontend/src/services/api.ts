import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Server {
  id: number;
  name: string;
  hostname: string;
  ip_address: string;
  status: string;
  server_type?: string;
  environment?: string;
  region?: string;
  specs?: Record<string, any>;
  metadata?: Record<string, any>;
  tags?: string[];
  tenant_id: string;
  created_at: string;
  updated_at?: string;
  version: number;
}

export interface ServerCreate {
  name: string;
  hostname: string;
  ip_address: string;
  server_type?: string;
  environment?: string;
  region?: string;
  specs?: Record<string, any>;
  metadata?: Record<string, any>;
  tags?: string[];
  tenant_id: string;
}

export interface ServerUpdate {
  name?: string;
  hostname?: string;
  ip_address?: string;
  status?: string;
  server_type?: string;
  environment?: string;
  region?: string;
  specs?: Record<string, any>;
  metadata?: Record<string, any>;
  tags?: string[];
}

export interface ServerListResponse {
  servers: Server[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const serverApi = {
  // Create server
  create: (server: ServerCreate): Promise<Server> =>
    api.post('/api/servers/', server).then(response => response.data),

  // List servers
  list: (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    environment?: string;
    region?: string;
    search?: string;
  }): Promise<ServerListResponse> =>
    api.get('/api/servers/', { params }).then(response => response.data),

  // Get server by ID
  get: (id: number): Promise<Server> =>
    api.get(`/api/servers/${id}`).then(response => response.data),

  // Update server
  update: (id: number, server: ServerUpdate): Promise<Server> =>
    api.put(`/api/servers/${id}`, server).then(response => response.data),

  // Delete server
  delete: (id: number): Promise<Server> =>
    api.delete(`/api/servers/${id}`).then(response => response.data),

  // Get audit logs
  getAuditLogs: (id: number): Promise<any[]> =>
    api.get(`/api/servers/${id}/audit`).then(response => response.data),
};
