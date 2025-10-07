import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  maxRedirects: 5,
  validateStatus: function (status) {
    return status >= 200 && status < 300; // default
  },
});

// Rules API
export const rulesAPI = {
  getRules: (params = {}) => api.get('/rules/', { params }),
  getRule: (id) => api.get(`/rules/${id}`),
  createRule: (data) => api.post('/rules/', data),
  updateRule: (id, data) => api.put(`/rules/${id}`, data),
  deleteRule: (id) => api.delete(`/rules/${id}`),
  bulkOperation: (data) => api.post('/rules/bulk', data),
  validateRule: (id) => api.get(`/rules/${id}/validate`),
};

// Templates API
export const templatesAPI = {
  getTemplates: (params = {}) => api.get('/templates/', { params }),
  getTemplate: (id) => api.get(`/templates/${id}`),
  createTemplate: (data) => api.post('/templates/', data),
  createRuleFromTemplate: (id, ruleName, overrides = {}) => 
    api.post(`/templates/${id}/create-rule`, null, {
      params: { rule_name: ruleName },
      data: overrides
    }),
  initializeDefaults: () => api.post('/templates/initialize-defaults'),
  getCategories: () => api.get('/templates/categories/list'),
};

// Testing API
export const testingAPI = {
  testRule: (data) => api.post('/test/rule', data),
  getTestHistory: (ruleId) => api.get(`/test/history/${ruleId}`),
  validateSyntax: (expression, thresholds) => 
    api.post('/test/validate', { expression, thresholds }),
  getExampleData: () => api.post('/test/example-data'),
};

export default api;
