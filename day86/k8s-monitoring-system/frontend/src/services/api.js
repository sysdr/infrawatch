import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const k8sApi = {
  getPods: (namespace = null, status = null) => {
    const params = {};
    if (namespace) params.namespace = namespace;
    if (status) params.status = status;
    return api.get('/k8s/pods', { params });
  },
  
  getServices: (namespace = null) => {
    const params = {};
    if (namespace) params.namespace = namespace;
    return api.get('/k8s/services', { params });
  },
  
  getDeployments: (namespace = null) => {
    const params = {};
    if (namespace) params.namespace = namespace;
    return api.get('/k8s/deployments', { params });
  },
  
  getNodes: () => api.get('/k8s/nodes'),
  
  getNamespaces: () => api.get('/k8s/namespaces'),
};

export const healthApi = {
  getCurrent: () => api.get('/health/current'),
  getHistory: (hours = 24) => api.get('/health/history', { params: { hours } }),
};

export const metricsApi = {
  getPodMetrics: (namespace, podName, hours = 1) => 
    api.get(`/metrics/pod/${namespace}/${podName}`, { params: { hours } }),
  
  getSummary: () => api.get('/metrics/summary'),
};

export default api;
