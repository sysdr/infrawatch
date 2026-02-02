import axios from 'axios';

const BACKEND_STORAGE_KEY = 'log_dashboard_backend_url';

/** Backend URL. Use same-origin (empty) so dev proxy forwards /api and /ws - works for localhost and WSL IP. Override via ?api= or localStorage. */
export function getApiBase() {
  if (typeof window !== 'undefined') {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get('api') || params.get('backend');
    if (fromQuery && (fromQuery.startsWith('http://') || fromQuery.startsWith('https://'))) {
      const base = fromQuery.replace(/\/+$/, '');
      try {
        localStorage.setItem(BACKEND_STORAGE_KEY, base);
      } catch (e) {}
      return base;
    }
    if (fromQuery === '' || fromQuery === 'same' || fromQuery === 'proxy') {
      try {
        localStorage.removeItem(BACKEND_STORAGE_KEY);
      } catch (e) {}
      return '';
    }
    try {
      const stored = localStorage.getItem(BACKEND_STORAGE_KEY);
      if (stored && stored.trim()) return stored.trim();
    } catch (e) {}
    // Same-origin: requests to /api/* go through setupProxy -> backend (works for localhost & WSL IP)
    return '';
  }
  if (typeof process !== 'undefined' && typeof process.env.REACT_APP_API_URL === 'string' && process.env.REACT_APP_API_URL.trim()) {
    return process.env.REACT_APP_API_URL.trim();
  }
  return 'http://localhost:8000';
}

/** Full URL for an API path. When base is '', returns path for same-origin (proxy). */
export function apiUrl(path) {
  const base = getApiBase().replace(/\/$/, '');
  const p = path.startsWith('/') ? path : '/' + path;
  return base ? base + p : p;
}

const instance = axios.create({
  headers: { 'Content-Type': 'application/json' },
  timeout: 8000, // fail fast when backend unreachable so dashboard still shows
});

instance.interceptors.request.use((config) => {
  const url = config.url || '';
  if (url.startsWith('http')) return config;
  config.url = apiUrl(url.startsWith('/') ? url : '/' + url);
  return config;
});

export const api = instance;
