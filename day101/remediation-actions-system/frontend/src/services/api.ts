import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';

export const api = {
  getTemplates: () => axios.get(`${API_BASE}/remediation/templates`),
  getActions: (status?: string) => axios.get(`${API_BASE}/remediation/actions`, { params: { status, limit: 100 } }),
  getAction: (id: number) => axios.get(`${API_BASE}/remediation/actions/${id}`),
  createAction: (data: any) => axios.post(`${API_BASE}/remediation/actions`, data),
  approveAction: (id: number, approver: string, comments: string) =>
    axios.post(`${API_BASE}/remediation/actions/${id}/approve`, { action_id: id, approver, comments }),
  rejectAction: (id: number) => axios.post(`${API_BASE}/remediation/actions/${id}/reject`),
  rollbackAction: (id: number) => axios.post(`${API_BASE}/remediation/actions/${id}/rollback`),
  getStats: () => axios.get(`${API_BASE}/remediation/stats`)
};
