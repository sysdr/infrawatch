import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Alert Rules
  getAlertRules: async () => {
    const response = await apiClient.get('/evaluation/rules');
    return response.data;
  },

  createAlertRule: async (rule) => {
    const response = await apiClient.post('/evaluation/rules', rule);
    return response.data;
  },

  // Active Alerts
  getActiveAlerts: async () => {
    const response = await apiClient.get('/evaluation/alerts/active');
    return response.data;
  },

  // Evaluation Metrics
  getEvaluationMetrics: async () => {
    const response = await apiClient.get('/evaluation/metrics/evaluation');
    return response.data;
  },

  // Manual Evaluation
  triggerEvaluation: async () => {
    const response = await apiClient.post('/evaluation/evaluate');
    return response.data;
  },

  // Test Anomaly Detection
  testAnomalyDetection: async () => {
    const response = await apiClient.post('/evaluation/test-anomaly');
    return response.data;
  },
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
