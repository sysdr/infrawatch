import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const metricsAPI = {
    createMetric: async (metricData) => {
        const response = await api.post('/api/metrics/definitions', metricData);
        return response.data;
    },
    
    listMetrics: async () => {
        const response = await api.get('/api/metrics/definitions');
        return response.data;
    },
    
    getMetric: async (metricId) => {
        const response = await api.get(`/api/metrics/definitions/${metricId}`);
        return response.data;
    },
    
    validateFormula: async (formula, variables) => {
        const response = await api.post('/api/metrics/validate-formula', {
            formula,
            variables,
        });
        return response.data;
    },
    
    calculateMetric: async (metricId, inputValues) => {
        const response = await api.post(`/api/metrics/calculate/${metricId}`, {
            input_values: inputValues,
        });
        return response.data;
    },
    
    getPerformance: async (metricId) => {
        const response = await api.get(`/api/metrics/performance/${metricId}`);
        return response.data;
    },
};

export default api;
