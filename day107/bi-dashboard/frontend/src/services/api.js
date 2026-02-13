import axios from 'axios';
const api = axios.create({ baseURL: '/api', headers: { 'Content-Type': 'application/json' } });
export const dashboardAPI = {
  getKPIs: () => api.get('/kpis').then(r => r.data),
  getKPIDetail: (metricName, days = 7) => api.get(`/kpis/${metricName}`, { params: { days } }).then(r => r.data),
  getTrendAnalysis: (metricName, windowDays = 30) => api.get(`/trends/${metricName}`, { params: { window_days: windowDays } }).then(r => r.data),
  getForecast: (metricName, days = 7, model = 'arima') => api.get(`/forecast/${metricName}`, { params: { days, model } }).then(r => r.data),
  compareByDimension: (metricName, dimension, periodDays = 30) => api.get('/compare/dimension', { params: { metric_name: metricName, dimension, period_days: periodDays } }).then(r => r.data),
  comparePeriods: (metricName, period1Days = 7, period2Days = 7) => api.get('/compare/periods', { params: { metric_name: metricName, period1_days: period1Days, period2_days: period2Days } }).then(r => r.data),
  getMetrics: () => api.get('/metrics').then(r => r.data),
  seedData: (days = 90) => api.post('/seed', null, { params: { days } }).then(r => r.data)
};
