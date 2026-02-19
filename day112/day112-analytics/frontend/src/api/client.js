import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 30000 })

export const fetchPipelineStatus  = () => api.get('/analytics/pipeline').then(r => r.data)
export const fetchEventSummary    = () => api.get('/analytics/summary').then(r => r.data)
export const postEvent            = (body) => api.post('/analytics/events', body).then(r => r.data)
export const fetchMLStatus        = () => api.get('/ml/status').then(r => r.data)
export const triggerTrain         = () => api.post('/ml/train').then(r => r.data)
export const fetchPredictions     = (h=24) => api.get(`/ml/predict?hours=${h}`).then(r => r.data)
export const fetchAnomalies       = () => api.get('/ml/anomalies').then(r => r.data)
export const fetchCorrelations    = (m='pearson') => api.get(`/ml/correlations?method=${m}`).then(r => r.data)
export const fetchKPIs            = () => api.get('/reports/kpis').then(r => r.data)
export const fetchReport          = (days=7) => api.get(`/reports/summary?days=${days}`).then(r => r.data)
