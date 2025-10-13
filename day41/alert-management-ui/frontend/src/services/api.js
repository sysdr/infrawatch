import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const alertService = {
  getAlerts: (filters = {}) => 
    api.get('/alerts/', { params: filters }).then(res => res.data),
  
  getAlert: (id) => 
    api.get(`/alerts/${id}`).then(res => res.data),
  
  acknowledgeAlert: (id) => 
    api.post(`/alerts/${id}/acknowledge`).then(res => res.data),
  
  resolveAlert: (id) => 
    api.post(`/alerts/${id}/resolve`).then(res => res.data),
  
  assignAlert: (id, assignee) => 
    api.post(`/alerts/${id}/assign`, { assignee }).then(res => res.data),
  
  bulkAction: (action, alertIds) => 
    api.post(`/alerts/bulk/${action}`, alertIds).then(res => res.data),
  
  getStats: () => 
    api.get('/alerts/stats/summary').then(res => res.data),
};

export const ruleService = {
  getRules: () => 
    api.get('/rules').then(res => res.data),
  
  createRule: (rule) => 
    api.post('/rules', rule).then(res => res.data),
  
  updateRule: (id, rule) => 
    api.put(`/rules/${id}`, rule).then(res => res.data),
  
  deleteRule: (id) => 
    api.delete(`/rules/${id}`).then(res => res.data),
  
  toggleRule: (id) => 
    api.post(`/rules/${id}/toggle`).then(res => res.data),
};
