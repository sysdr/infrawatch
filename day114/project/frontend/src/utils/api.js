import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

export const fetchSummary   = (hours = 24) => api.get(`/api/metrics/summary?hours=${hours}`).then(r => r.data);
export const fetchTimeseries = (metric, hours = 6) =>
  api.get(`/api/metrics/timeseries/${metric}?hours=${hours}`).then(r => r.data);

export default api;
