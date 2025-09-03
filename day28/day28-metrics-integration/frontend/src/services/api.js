import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Create metric
  async createMetric(metric) {
    const response = await this.client.post('/metrics', metric);
    return response.data;
  }

  // Create metrics batch
  async createMetricsBatch(metrics) {
    const response = await this.client.post('/metrics/batch', { metrics });
    return response.data;
  }

  // Query metrics
  async queryMetrics(params = {}) {
    const response = await this.client.get('/metrics', { params });
    return response.data;
  }

  // Get realtime metrics
  async getRealtimeMetrics() {
    const response = await this.client.get('/metrics/realtime');
    return response.data;
  }

  // Get metric summary
  async getMetricSummary(name, hours = 24) {
    const response = await this.client.get(`/metrics/${name}/summary`, {
      params: { hours }
    });
    return response.data;
  }

  // Server-Sent Events connection
  createSSEConnection(onMessage, onError) {
    const eventSource = new EventSource(`${API_BASE}/stream`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('SSE Parse Error:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      onError(error);
    };

    return eventSource;
  }
}

export default new ApiService();
