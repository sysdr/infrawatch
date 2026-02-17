import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const apiService = {
  // Dashboard
  getDashboardSummary: async () => {
    const response = await apiClient.get('/api/correlation/dashboard/summary');
    return response.data;
  },

  // Metrics
  generateSampleMetrics: async () => {
    const response = await apiClient.post('/api/correlation/metrics/generate-sample');
    return response.data;
  },

  // Correlations
  getCorrelations: async (state = null) => {
    const params = state ? { state } : {};
    const response = await apiClient.get('/api/correlation/correlations', { params });
    return response.data;
  },

  detectCorrelations: async () => {
    const response = await apiClient.post('/api/correlation/detect');
    return response.data;
  },

  // Root Cause Analysis
  analyzeRootCause: async () => {
    const response = await apiClient.post('/api/correlation/analyze/root-cause');
    return response.data;
  },

  // Impact Assessment
  analyzeImpact: async (metricId) => {
    const response = await apiClient.post(`/api/correlation/analyze/impact/${metricId}`);
    return response.data;
  },
};

export default apiService;
