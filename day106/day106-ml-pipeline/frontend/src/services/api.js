import axios from 'axios'

const BASE = '/api/v1/ml'

export const api = {
  health: () => axios.get('/api/v1/health'),
  status: () => axios.get(`${BASE}/status`),
  train: (n = 500) => axios.post(`${BASE}/train?n_samples=${n}`),
  latestAnomaly: () => axios.get(`${BASE}/anomalies/latest`),
  batchAnomalies: (n = 80) => axios.get(`${BASE}/anomalies/batch?n_points=${n}`),
  forecast: (metric = 'cpu_usage') => axios.get(`${BASE}/forecast?metric=${metric}`),
  allForecasts: () => axios.get(`${BASE}/forecast/all`),
  patterns: () => axios.get(`${BASE}/patterns`),
  evaluation: () => axios.get(`${BASE}/evaluation`),
}
