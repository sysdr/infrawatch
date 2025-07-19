import axios from 'axios';
import { tokenManager } from './tokenManager';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

class AuthService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      timeout: parseInt(process.env.REACT_APP_API_TIMEOUT) || 10000,
      withCredentials: true, // Important for httpOnly cookies
    });

    this.isRefreshing = false;
    this.setupInterceptors();
  }

  setupInterceptors() {
    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = tokenManager.getAccessToken();
        if (token && !tokenManager.isTokenExpired(token)) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for automatic token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Only attempt token refresh for 401 errors on non-auth endpoints
        if (error.response?.status === 401 && 
            !originalRequest._retry && 
            !this.isRefreshing &&
            !originalRequest.url?.includes('/auth/refresh') &&
            !originalRequest.url?.includes('/auth/login') &&
            !originalRequest.url?.includes('/auth/register')) {
          
          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const newTokens = await this.refreshToken();
            tokenManager.setTokens(newTokens);
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
            this.isRefreshing = false;
            return this.api(originalRequest);
          } catch (refreshError) {
            this.isRefreshing = false;
            // Only redirect to login if we're not already on an auth page
            if (!window.location.pathname.includes('/login') && 
                !window.location.pathname.includes('/register')) {
              tokenManager.removeTokens();
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  async login(credentials) {
    try {
      const response = await this.api.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async register(userData) {
    try {
      const response = await this.api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async logout() {
    try {
      await this.api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  async refreshToken() {
    try {
      // Check if we have a refresh token before making the request
      const hasRefreshToken = document.cookie.includes('refresh_token=');
      if (!hasRefreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await this.api.post('/auth/refresh');
      return response.data;
    } catch (error) {
      throw new Error('Token refresh failed');
    }
  }

  async getCurrentUser() {
    try {
      const response = await this.api.get('/users/me');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get user profile');
    }
  }

  async verifyToken() {
    try {
      const token = tokenManager.getAccessToken();
      const response = await this.api.get(`/auth/verify?token=${token}`);
      return response.data;
    } catch (error) {
      throw new Error('Token verification failed');
    }
  }
}

export const authService = new AuthService();
