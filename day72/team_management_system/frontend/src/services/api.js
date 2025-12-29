import axios from 'axios';

// Determine API base URL based on current hostname
// If accessing via WSL2 IP, use WSL2 IP for backend; otherwise use localhost
const getApiBase = () => {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  
  const hostname = window.location.hostname;
  const port = window.location.port || '3000';
  console.log(`[API] Current location: ${window.location.href}`);
  console.log(`[API] Current hostname: ${hostname}, port: ${port}`);
  
  // If accessing via IP address (WSL2), use same IP for backend
  // Check for IP pattern (e.g., 172.22.24.182)
  const ipPattern = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
  if (hostname && ipPattern.test(hostname)) {
    const apiBase = `http://${hostname}:8000`;
    console.log(`[API] Detected IP address, using WSL2 backend URL: ${apiBase}`);
    return apiBase;
  }
  
  // If not localhost, use the hostname
  if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
    const apiBase = `http://${hostname}:8000`;
    console.log(`[API] Using hostname backend URL: ${apiBase}`);
    return apiBase;
  }
  
  const apiBase = 'http://localhost:8000';
  console.log(`[API] Using localhost backend URL: ${apiBase}`);
  return apiBase;
};

// Compute API base dynamically each time (not just at module load)
const getApiBaseUrl = () => getApiBase();

// For backward compatibility, also export a constant (but it will be recomputed)
let API_BASE = getApiBase();
console.log(`[API] Initial API Base URL: ${API_BASE}`);

// Update API_BASE when window location changes (for SPA navigation)
if (typeof window !== 'undefined') {
  // Recompute on any navigation
  const originalPushState = history.pushState;
  history.pushState = function(...args) {
    API_BASE = getApiBase();
    console.log(`[API] Updated API Base URL: ${API_BASE}`);
    return originalPushState.apply(history, args);
  };
}

// Create axios instance with error handling
// baseURL will be set dynamically in request interceptor
const apiClient = axios.create({
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Override request interceptor to always use current API base
apiClient.interceptors.request.use((config) => {
  // Force recomputation on every request - NEVER use cached baseURL
  const currentApiBase = getApiBase();
  
  // CRITICAL: Always override baseURL to prevent using cached localhost
  config.baseURL = currentApiBase;
  
  // Log for debugging
  console.log(`[API] ========================================`);
  console.log(`[API] Request: ${config.method?.toUpperCase()} ${config.url}`);
  console.log(`[API] Full URL: ${currentApiBase}${config.url}`);
  console.log(`[API] Origin: ${window.location.origin}`);
  console.log(`[API] Hostname: ${window.location.hostname}`);
  console.log(`[API] ========================================`);
  
  return config;
});

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only log errors in development, and only once per error type
    if (process.env.NODE_ENV === 'development') {
      if (error.response) {
        // Log 400/500 errors with details
        if (error.response.status >= 400) {
          console.error(`API Error ${error.response.status}:`, error.response.data);
        }
      } else if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
        const currentApiBase = getApiBaseUrl();
        console.error(`Connection Error: Backend server not reachable at ${currentApiBase}`);
      }
    }
    
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
      const currentApiBase = getApiBaseUrl();
      error.message = `Cannot connect to backend server. Please ensure the backend is running on ${currentApiBase}`;
    }
    
    // Ensure error.response.data is accessible
    if (error.response && error.response.data) {
      // If detail is an array (validation errors), format it
      if (Array.isArray(error.response.data.detail)) {
        error.formattedMessage = error.response.data.detail
          .map(err => `${err.loc?.join('.')}: ${err.msg}`)
          .join(', ');
      } else if (error.response.data.detail) {
        error.formattedMessage = error.response.data.detail;
      }
    }
    
    return Promise.reject(error);
  }
);

export const createOrganization = async (data) => {
  const response = await apiClient.post('/api/teams/organizations', data);
  return response.data;
};

export const createRole = async (data) => {
  const response = await apiClient.post('/api/teams/roles', data);
  return response.data;
};

export const createTeam = async (data) => {
  const response = await apiClient.post('/api/teams', data);
  return response.data;
};

export const addTeamMember = async (teamId, data) => {
  const response = await apiClient.post(`/api/teams/${teamId}/members`, data);
  return response.data;
};

export const getTeamDashboard = async (teamId) => {
  const response = await apiClient.get(`/api/teams/${teamId}/dashboard`);
  return response.data;
};

export const getTeamMembers = async (teamId) => {
  const response = await apiClient.get(`/api/teams/${teamId}/members`);
  return response.data;
};

export const connectTeamWebSocket = (teamId, onMessage) => {
  // Use same hostname as API base for WebSocket
  const currentApiBase = getApiBaseUrl();
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = currentApiBase.replace(/^https?:\/\//, '').replace(':8000', '');
  const ws = new WebSocket(`${wsProtocol}//${wsHost}:8000/ws/teams/${teamId}?user_id=1`);
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  return ws;
};
