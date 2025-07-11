import axios from 'axios';
import Cookies from 'js-cookie';
import { AuthResponse, LoginCredentials, RegisterCredentials, User } from '../types/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const authAPI = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Request interceptor to add auth token
authAPI.interceptors.request.use((config) => {
  const token = Cookies.get('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
authAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = Cookies.get('refreshToken');
      if (refreshToken) {
        try {
          const response = await authAPI.post('/auth/refresh', { refreshToken });
          const { accessToken } = response.data;
          Cookies.set('accessToken', accessToken, { expires: 1 });
          error.config.headers.Authorization = `Bearer ${accessToken}`;
          return authAPI.request(error.config);
        } catch (refreshError) {
          Cookies.remove('accessToken');
          Cookies.remove('refreshToken');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // For demo purposes, simulate a successful login
    if (credentials.email === 'demo@example.com' && credentials.password === 'password123') {
      const mockResponse: AuthResponse = {
        user: {
          id: '1',
          email: 'demo@example.com',
          name: 'Demo User',
          role: 'user',
          createdAt: new Date().toISOString(),
        },
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
      };
      
      Cookies.set('accessToken', mockResponse.accessToken, { expires: 1 });
      Cookies.set('refreshToken', mockResponse.refreshToken, { expires: 7 });
      
      return mockResponse;
    }
    
    throw new Error('Invalid credentials. Use demo@example.com / password123');
  },

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    const response = await authAPI.post('/auth/register', credentials);
    const { user, accessToken, refreshToken } = response.data;
    
    Cookies.set('accessToken', accessToken, { expires: 1 });
    Cookies.set('refreshToken', refreshToken, { expires: 7 });
    
    return { user, accessToken, refreshToken };
  },

  async logout(): Promise<void> {
    try {
      await authAPI.post('/auth/logout');
    } finally {
      Cookies.remove('accessToken');
      Cookies.remove('refreshToken');
    }
  },

  async getCurrentUser(): Promise<User> {
    // For demo purposes, return mock user if token exists
    const token = Cookies.get('accessToken');
    if (token === 'mock-access-token') {
      return {
        id: '1',
        email: 'demo@example.com',
        name: 'Demo User',
        role: 'user',
        createdAt: new Date().toISOString(),
      };
    }
    
    const response = await authAPI.get('/auth/me');
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    // For demo purposes, return updated mock user
    const token = Cookies.get('accessToken');
    if (token === 'mock-access-token') {
      return {
        id: '1',
        email: data.email || 'demo@example.com',
        name: data.name || 'Demo User',
        role: 'user',
        createdAt: new Date().toISOString(),
      };
    }
    
    const response = await authAPI.put('/auth/profile', data);
    return response.data;
  },

  getStoredToken(): string | undefined {
    return Cookies.get('accessToken');
  }
};
