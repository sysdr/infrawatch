import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const alertAPI = {
    getAllAlerts: () => api.get('/alerts'),
    getFiringAlerts: () => api.get('/alerts/firing'),
    getAlert: (id) => api.get(`/alerts/${id}`),
    getRules: () => api.get('/rules'),
    createRule: (rule) => api.post('/rules', rule),
    ingestMetrics: (metrics) => api.post('/metrics', metrics),
    healthCheck: () => api.get('/health'),
};

export default api;
