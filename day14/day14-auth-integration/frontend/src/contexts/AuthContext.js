import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/authService';
import { tokenManager } from '../services/tokenManager';

const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, loading: true, error: null };
    case 'AUTH_SUCCESS':
      return { 
        ...state, 
        loading: false, 
        user: action.payload.user, 
        isAuthenticated: true,
        error: null 
      };
    case 'AUTH_FAILURE':
      return { 
        ...state, 
        loading: false, 
        user: null, 
        isAuthenticated: false,
        error: action.payload 
      };
    case 'LOGOUT':
      return { 
        ...state, 
        user: null, 
        isAuthenticated: false, 
        loading: false,
        error: null 
      };
    case 'TOKEN_REFRESH_START':
      return { ...state, refreshing: true };
    case 'TOKEN_REFRESH_SUCCESS':
      return { ...state, refreshing: false };
    case 'TOKEN_REFRESH_FAILURE':
      return { 
        ...state, 
        refreshing: false, 
        user: null, 
        isAuthenticated: false 
      };
    case 'INIT_COMPLETE':
      return { ...state, loading: false };
    default:
      return state;
  }
};

const initialState = {
  user: null,
  isAuthenticated: false,
  loading: true, // Start with loading true
  refreshing: false,
  error: null
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    // Check for existing session on app load
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const token = tokenManager.getAccessToken();
      
      // If no token exists, just complete initialization
      if (!token) {
        dispatch({ type: 'INIT_COMPLETE' });
        return;
      }

      // If token is expired, remove it and complete initialization
      if (tokenManager.isTokenExpired(token)) {
        tokenManager.removeTokens();
        dispatch({ type: 'INIT_COMPLETE' });
        return;
      }

      // Try to get user profile with valid token
      try {
        const userProfile = await authService.getCurrentUser();
        dispatch({ type: 'AUTH_SUCCESS', payload: { user: userProfile } });
      } catch (error) {
        // If getting user profile fails, remove tokens and complete initialization
        console.log('Failed to get user profile during initialization:', error.message);
        tokenManager.removeTokens();
        dispatch({ type: 'INIT_COMPLETE' });
      }
    } catch (error) {
      // Handle any other errors during initialization
      console.error('Auth initialization error:', error);
      tokenManager.removeTokens();
      dispatch({ type: 'INIT_COMPLETE' });
    }
  };

  const login = async (credentials) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authService.login(credentials);
      tokenManager.setTokens(response.tokens);
      dispatch({ type: 'AUTH_SUCCESS', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE', payload: error.message });
      throw error;
    }
  };

  const register = async (userData) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authService.register(userData);
      tokenManager.setTokens(response.tokens);
      dispatch({ type: 'AUTH_SUCCESS', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE', payload: error.message });
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      tokenManager.removeTokens();
      dispatch({ type: 'LOGOUT' });
    }
  };

  const refreshToken = async () => {
    dispatch({ type: 'TOKEN_REFRESH_START' });
    try {
      const newTokens = await authService.refreshToken();
      tokenManager.setTokens(newTokens);
      dispatch({ type: 'TOKEN_REFRESH_SUCCESS' });
      return newTokens;
    } catch (error) {
      dispatch({ type: 'TOKEN_REFRESH_FAILURE' });
      throw error;
    }
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    refreshToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
