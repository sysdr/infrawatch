import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || error.message);
  }
);

export const getHealthStatus = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const getHelloWorld = async () => {
  const response = await apiClient.get('/api/hello');
  return response.data;
};

export const echoMessage = async (data) => {
  const response = await apiClient.post('/api/echo', data);
  return response.data;
};

export const getStatus = async () => {
  const response = await apiClient.get('/api/status');
  return response.data;
};

export default apiClient;
