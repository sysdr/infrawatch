import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const alertService = {
  async getAlertRules() {
    const response = await api.get('/api/alert-rules/');
    return response.data;
  },

  async createAlertRule(ruleData: any) {
    const response = await api.post('/api/alert-rules/', ruleData);
    return response.data;
  },

  async getActiveAlerts() {
    const response = await api.get('/api/alert-rules/instances/active');
    return response.data;
  },

  async acknowledgeAlert(instanceId: number) {
    const response = await api.post(`/api/alert-rules/instances/${instanceId}/acknowledge`);
    return response.data;
  },
};
