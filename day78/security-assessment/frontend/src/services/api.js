import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/security';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const securityAPI = {
  // Scan operations
  runVulnerabilityScan: (directory = '/tmp/scan_target') =>
    api.post('/scan/vulnerability', { directory }),
  
  runCodeAnalysis: (directory = '/tmp/scan_target') =>
    api.post('/scan/code-analysis', { directory }),
  
  runDependencyAudit: (directory = '/tmp/scan_target') =>
    api.post('/scan/dependencies', { directory }),
  
  runComplianceCheck: (directory = '/tmp/scan_target') =>
    api.post('/scan/compliance', { directory }),
  
  runThreatModel: (directory = '/tmp/scan_target') =>
    api.post('/scan/threat-model', { directory }),
  
  runFullScan: (directory = '/tmp/scan_target') =>
    api.post('/scan/full', { directory }),
  
  // Results retrieval
  getVulnerabilities: (severity = null, limit = 100) =>
    api.get('/results/vulnerabilities', { params: { severity, limit } }),
  
  getComplianceResults: (framework = null) =>
    api.get('/results/compliance', { params: { framework } }),
  
  getThreatModel: (component = null) =>
    api.get('/results/threats', { params: { component } }),
  
  getDashboardMetrics: () =>
    api.get('/dashboard/metrics'),
};

export default api;
