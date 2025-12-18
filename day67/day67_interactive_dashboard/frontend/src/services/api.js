import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export const dashboardAPI = {
  getMetrics: (params) => 
    api.get('/dashboard/metrics', { params }).then(res => res.data),
  
  getAggregated: (params) => 
    api.get('/dashboard/aggregated', { params }).then(res => res.data),
  
  getTimeSeries: (params) => 
    api.get('/dashboard/timeseries', { params }).then(res => res.data),
}

export const filtersAPI = {
  getAvailable: (params) => 
    api.get('/filters/available', { params }).then(res => res.data),
  
  getCounts: (params) => 
    api.get('/filters/counts', { params }).then(res => res.data),
}

export const drilldownAPI = {
  getHierarchy: () => 
    api.get('/drilldown/hierarchy').then(res => res.data),
  
  navigate: (data) => 
    api.post('/drilldown/navigate', data).then(res => res.data),
  
  getDetails: (params) => 
    api.get('/drilldown/details', { params }).then(res => res.data),
}

export default api
