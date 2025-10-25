import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Templates API
export const fetchTemplates = async () => {
  const response = await api.get('/templates/');
  return response.data;
};

export const fetchTemplate = async (templateId) => {
  const response = await api.get(`/templates/${templateId}`);
  return response.data;
};

export const renderTemplate = async (request) => {
  const response = await api.post('/templates/render', request);
  return response.data;
};

export const validateTemplate = async (templateId) => {
  const response = await api.get(`/templates/${templateId}/validate`);
  return response.data;
};

// Testing API
export const getSampleData = async () => {
  const response = await api.get('/test/sample-data');
  return response.data;
};

export const testRenderAll = async () => {
  const response = await api.post('/test/render-all');
  return response.data;
};

export default api;
