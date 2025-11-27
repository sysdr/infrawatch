import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const createExport = async (exportRequest) => {
  const response = await api.post('/api/exports/create', exportRequest);
  return response.data;
};

export const getExportStatus = async (jobId) => {
  const response = await api.get(`/api/exports/${jobId}/status`);
  return response.data;
};

export const getExports = async (userId = null, limit = 20) => {
  const params = { limit };
  if (userId) params.user_id = userId;
  
  const response = await api.get('/api/exports/list', { params });
  return response.data;
};

export const downloadExport = async (jobId) => {
  const response = await api.get(`/api/exports/${jobId}/download`, {
    responseType: 'blob'
  });
  
  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  
  // Get filename from content-disposition header or use default
  const contentDisposition = response.headers['content-disposition'];
  const filename = contentDisposition
    ? contentDisposition.split('filename=')[1].replace(/"/g, '')
    : `export_${jobId}.file`;
    
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export default api;
