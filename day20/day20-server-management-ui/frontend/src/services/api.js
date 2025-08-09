import axios from 'axios';

const client = axios.create({ baseURL: '/api' });

export const serverAPI = {
  async getServers(filters = {}) {
    const params = {
      page: filters.page ?? 1,
      page_size: filters.pageSize ?? 50,
      search: filters.search || undefined,
      status: filters.status || undefined,
      server_type: filters.serverType || undefined,
    };
    const { data } = await client.get('/servers/', { params });
    return data;
  },
  async getMetrics() {
    const { data } = await client.get('/servers/metrics');
    return data;
  },
  async createServer(payload) {
    const { data } = await client.post('/servers/', payload);
    return data;
  },
  async updateServer(id, payload) {
    const { data } = await client.put(`/servers/${id}`, payload);
    return data;
  },
  async deleteServer(id) {
    await client.delete(`/servers/${id}`);
  },
  async bulkAction(payload) {
    const { data } = await client.post('/servers/bulk-action', payload);
    return data;
  },
};
