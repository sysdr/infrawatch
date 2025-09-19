import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const fetchTasks = async (params = {}) => {
  const response = await api.get('/tasks', { params });
  return response.data;
};

export const createTask = async (taskData) => {
  const response = await api.post('/tasks', taskData);
  return response.data;
};

export const retryTask = async (taskId) => {
  const response = await api.post(`/tasks/${taskId}/retry`);
  return response.data;
};

export const cancelTask = async (taskId) => {
  const response = await api.delete(`/tasks/${taskId}`);
  return response.data;
};

export default api;
