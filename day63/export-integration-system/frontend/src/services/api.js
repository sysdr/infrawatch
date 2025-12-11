import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const exportAPI = {
    // Export jobs
    createExport: (data) => api.post('/api/exports', data),
    listExports: (skip = 0, limit = 20) => api.get(`/api/exports?skip=${skip}&limit=${limit}`),
    getExport: (jobId) => api.get(`/api/exports/${jobId}`),
    downloadExport: (jobId) => `${API_BASE_URL}/api/exports/${jobId}/download`,
    
    // Schedules
    createSchedule: (data) => api.post('/api/schedules', data),
    listSchedules: () => api.get('/api/schedules'),
    deleteSchedule: (scheduleId) => api.delete(`/api/schedules/${scheduleId}`),
    getScheduleHistory: (scheduleId) => api.get(`/api/schedules/${scheduleId}/history`),
    
    // Stats
    getStats: () => api.get('/api/stats'),
};

export default api;
