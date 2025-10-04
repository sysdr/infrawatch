import axios from 'axios';

const API_BASE_URL = '/api/v1';

class AlertService {
  static async getAlerts(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    
    const response = await axios.get(`${API_BASE_URL}/alerts?${params.toString()}`);
    return response.data;
  }

  static async getAlert(id) {
    const response = await axios.get(`${API_BASE_URL}/alerts/${id}`);
    return response.data;
  }

  static async createAlert(alertData) {
    const response = await axios.post(`${API_BASE_URL}/alerts`, alertData);
    return response.data;
  }

  static async acknowledgeAlert(id, acknowledgedBy) {
    const response = await axios.post(`${API_BASE_URL}/alerts/${id}/acknowledge`, {
      acknowledged_by: acknowledgedBy
    });
    return response.data;
  }

  static async resolveAlert(id, resolvedBy) {
    const response = await axios.post(`${API_BASE_URL}/alerts/${id}/resolve`, {
      resolved_by: resolvedBy
    });
    return response.data;
  }

  static async getStats() {
    const response = await axios.get(`${API_BASE_URL}/alerts/stats/summary`);
    return response.data;
  }

  static async getAlertHistory(id) {
    const response = await axios.get(`${API_BASE_URL}/alerts/history/${id}`);
    return response.data;
  }
}

export default AlertService;
