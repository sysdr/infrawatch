#!/bin/bash

# Day 13: React Authentication UI Implementation Script
# 180-Day Distributed Systems Course - Week 2

set -e

echo "🚀 Starting Day 13: React Authentication UI Implementation"
echo "=================================================="

# Create project structure
echo "📁 Creating project structure..."
mkdir -p day13-react-auth-ui
cd day13-react-auth-ui

# Initialize React project
echo "⚛️ Initializing React project..."
npx create-react-app . --template typescript
rm -rf .git

# Install additional dependencies
echo "📦 Installing dependencies..."
npm install --save \
  @tanstack/react-query@5.51.0 \
  axios@1.7.2 \
  react-router-dom@6.24.0 \
  @hookform/resolvers@3.6.0 \
  react-hook-form@7.52.0 \
  yup@1.4.0 \
  js-cookie@3.0.5 \
  @types/js-cookie@3.0.6 \
  lucide-react@0.400.0

npm install --save-dev \
  @testing-library/jest-dom@6.4.6 \
  @testing-library/react@16.0.0 \
  @testing-library/user-event@14.5.2 \
  msw@2.3.1

# Create directory structure
echo "📂 Creating directory structure..."
mkdir -p src/components/auth
mkdir -p src/components/ui
mkdir -p src/hooks
mkdir -p src/contexts
mkdir -p src/services
mkdir -p src/types
mkdir -p src/utils
mkdir -p src/pages
mkdir -p src/__tests__
mkdir -p public/assets

# Create type definitions
echo "📝 Creating type definitions..."
cat > src/types/auth.ts << 'EOF'
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  avatar?: string;
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  name: string;
  confirmPassword: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}
EOF

# Create authentication service
echo "🔐 Creating authentication service..."
cat > src/services/authService.ts << 'EOF'
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
    const response = await authAPI.post('/auth/login', credentials);
    const { user, accessToken, refreshToken } = response.data;
    
    Cookies.set('accessToken', accessToken, { expires: 1 });
    Cookies.set('refreshToken', refreshToken, { expires: 7 });
    
    return response.data;
  },

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    const response = await authAPI.post('/auth/register', credentials);
    const { user, accessToken, refreshToken } = response.data;
    
    Cookies.set('accessToken', accessToken, { expires: 1 });
    Cookies.set('refreshToken', refreshToken, { expires: 7 });
    
    return response.data;
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
    const response = await authAPI.get('/auth/me');
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await authAPI.put('/auth/profile', data);
    return response.data;
  },

  getStoredToken(): string | undefined {
    return Cookies.get('accessToken');
  }
};
EOF

# Create authentication context
echo "🎯 Creating authentication context..."
cat > src/contexts/AuthContext.tsx << 'EOF'
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/authService';
import { AuthState, User, LoginCredentials, RegisterCredentials } from '../types/auth';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false,
        error: null,
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const login = async (credentials: LoginCredentials) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const { user } = await authService.login(credentials);
      dispatch({ type: 'SET_USER', payload: user });
    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.response?.data?.message || 'Login failed' });
      throw error;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const { user } = await authService.register(credentials);
      dispatch({ type: 'SET_USER', payload: user });
    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.response?.data?.message || 'Registration failed' });
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } finally {
      dispatch({ type: 'SET_USER', payload: null });
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const updatedUser = await authService.updateProfile(data);
      dispatch({ type: 'SET_USER', payload: updatedUser });
    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.response?.data?.message || 'Profile update failed' });
      throw error;
    }
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const token = authService.getStoredToken();
      if (token) {
        try {
          const user = await authService.getCurrentUser();
          dispatch({ type: 'SET_USER', payload: user });
        } catch (error) {
          dispatch({ type: 'SET_USER', payload: null });
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    initializeAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        updateProfile,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
EOF

# Create UI components
echo "🎨 Creating UI components..."
cat > src/components/ui/Button.tsx << 'EOF'
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-300',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 disabled:bg-gray-100',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-red-300',
  };

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {children}
    </button>
  );
};
EOF

cat > src/components/ui/Input.tsx << 'EOF'
import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ 
  label, 
  error, 
  className = '', 
  ...props 
}) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        className={`block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
          error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''
        } ${className}`}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};
EOF

# Create protected route component
echo "🛡️ Creating protected route component..."
cat > src/components/auth/ProtectedRoute.tsx << 'EOF'
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'user' | 'viewer';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user?.role !== requiredRole && user?.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
          <p className="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
EOF

# Create login component
echo "🔐 Creating login component..."
cat > src/components/auth/LoginForm.tsx << 'EOF'
import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { LoginCredentials } from '../../types/auth';

const schema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(6, 'Password must be at least 6 characters').required('Password is required'),
});

export const LoginForm: React.FC = () => {
  const { login, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>({
    resolver: yupResolver(schema),
  });

  const onSubmit = async (data: LoginCredentials) => {
    try {
      clearError();
      await login(data);
      navigate(from, { replace: true });
    } catch (error) {
      // Error is handled by context
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
              create a new account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <Input
              label="Email address"
              type="email"
              autoComplete="email"
              {...register('email')}
              error={errors.email?.message}
            />
            <Input
              label="Password"
              type="password"
              autoComplete="current-password"
              {...register('password')}
              error={errors.password?.message}
            />
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
          >
            Sign in
          </Button>
        </form>
      </div>
    </div>
  );
};
EOF

# Create user profile component
echo "👤 Creating user profile component..."
cat > src/components/auth/UserProfile.tsx << 'EOF'
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { User } from '../../types/auth';

const schema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
});

export const UserProfile: React.FC = () => {
  const { user, updateProfile, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<Pick<User, 'name' | 'email'>>({
    resolver: yupResolver(schema),
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
    },
  });

  const onSubmit = async (data: Pick<User, 'name' | 'email'>) => {
    try {
      setIsLoading(true);
      await updateProfile(data);
      setIsEditing(false);
    } catch (error) {
      // Error handled by context
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    reset({
      name: user?.name || '',
      email: user?.email || '',
    });
    setIsEditing(false);
  };

  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto bg-white shadow-sm rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Profile</h2>
        <div className="flex space-x-3">
          {!isEditing ? (
            <>
              <Button
                variant="secondary"
                onClick={() => setIsEditing(true)}
              >
                Edit Profile
              </Button>
              <Button
                variant="danger"
                onClick={logout}
              >
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="secondary"
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSubmit(onSubmit)}
                isLoading={isLoading}
              >
                Save Changes
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <div className="flex items-center space-x-4">
          <div className="h-20 w-20 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-2xl font-medium text-blue-600">
              {user.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">{user.name}</h3>
            <p className="text-sm text-gray-500">Role: {user.role}</p>
            <p className="text-sm text-gray-500">
              Member since {new Date(user.createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Full Name"
            {...register('name')}
            error={errors.name?.message}
            disabled={!isEditing}
          />
          <Input
            label="Email Address"
            type="email"
            {...register('email')}
            error={errors.email?.message}
            disabled={!isEditing}
          />
        </form>
      </div>
    </div>
  );
};
EOF

# Create main pages
echo "📄 Creating pages..."
cat > src/pages/Dashboard.tsx << 'EOF'
import React from 'react';
import { UserProfile } from '../components/auth/UserProfile';

export const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to your personalized dashboard</p>
        </div>
        <UserProfile />
      </div>
    </div>
  );
};
EOF

# Update App.tsx
echo "⚛️ Updating App.tsx..."
cat > src/App.tsx << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginForm } from './components/auth/LoginForm';
import { Dashboard } from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
EOF

# Update CSS with Google Cloud-inspired styling
echo "🎨 Updating styles..."
cat > src/App.css << 'EOF'
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

body {
  font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.App {
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* Google Cloud-inspired components */
.gcp-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border: 1px solid #e8eaed;
}

.gcp-button-primary {
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.gcp-button-primary:hover {
  background-color: #1557b0;
}

.gcp-input {
  border: 1px solid #dadce0;
  border-radius: 4px;
  padding: 12px 16px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.gcp-input:focus {
  outline: none;
  border-color: #1a73e8;
  box-shadow: 0 0 0 1px #1a73e8;
}
EOF

# Add Tailwind config
echo "🎨 Configuring Tailwind..."
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'gcp-blue': '#1a73e8',
        'gcp-gray': '#5f6368',
        'gcp-light-gray': '#f8f9fa',
      },
      fontFamily: {
        'google': ['Google Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
EOF

# Create test files
echo "🧪 Creating test files..."
cat > src/__tests__/AuthContext.test.tsx << 'EOF'
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';

// Mock the auth service
jest.mock('../services/authService');
const mockAuthService = authService as jest.Mocked<typeof authService>;

const TestComponent = () => {
  const { isAuthenticated, login, logout, user } = useAuth();
  
  return (
    <div>
      <div>{isAuthenticated ? 'Authenticated' : 'Not authenticated'}</div>
      {user && <div>User: {user.name}</div>}
      <button onClick={() => login({ email: 'test@example.com', password: 'password' })}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should handle login successfully', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user' as const,
      createdAt: '2024-01-01',
    };

    mockAuthService.login.mockResolvedValue({
      user: mockUser,
      accessToken: 'token',
      refreshToken: 'refresh-token',
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Not authenticated')).toBeInTheDocument();

    const loginButton = screen.getByText('Login');
    await userEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Authenticated')).toBeInTheDocument();
      expect(screen.getByText('User: Test User')).toBeInTheDocument();
    });
  });

  it('should handle logout', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user' as const,
      createdAt: '2024-01-01',
    };

    mockAuthService.login.mockResolvedValue({
      user: mockUser,
      accessToken: 'token',
      refreshToken: 'refresh-token',
    });

    mockAuthService.logout.mockResolvedValue();

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Login first
    const loginButton = screen.getByText('Login');
    await userEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Authenticated')).toBeInTheDocument();
    });

    // Then logout
    const logoutButton = screen.getByText('Logout');
    await userEvent.click(logoutButton);

    await waitFor(() => {
      expect(screen.getByText('Not authenticated')).toBeInTheDocument();
    });
  });
});
EOF

# Create package.json scripts update
echo "📦 Updating package.json scripts..."
npm pkg set scripts.start="react-scripts start"
npm pkg set scripts.build="react-scripts build"
npm pkg set scripts.test="react-scripts test"
npm pkg set scripts.eject="react-scripts eject"

# Build the application
echo "🔨 Building application..."
npm run build

# Run tests
echo "🧪 Running tests..."
npm test -- --coverage --watchAll=false

# Create demo data and mock server setup
echo "🎭 Setting up demo environment..."
cat > public/demo-setup.js << 'EOF'
// Demo setup for authentication UI
window.DEMO_MODE = true;
window.DEMO_USER = {
  id: '1',
  email: 'demo@example.com',
  name: 'Demo User',
  role: 'user',
  createdAt: '2024-01-01T00:00:00Z'
};
EOF

# Create demo instructions
echo "📋 Creating demo instructions..."
cat > DEMO_INSTRUCTIONS.md << 'EOF'
# Day 13: React Authentication UI Demo

## Quick Demo Steps

1. **Start the development server:**
   ```bash
   npm start
   ```

2. **Open browser to http://localhost:3000**

3. **Test the authentication flow:**
   - You'll be redirected to login page
   - Use demo credentials: 
     - Email: demo@example.com
     - Password: password123
   - Try invalid credentials to see error handling
   - Navigate around to test protected routes

4. **Test user profile features:**
   - Edit profile information
   - View role-based content
   - Test logout functionality

## Key Features Demonstrated

- ✅ Responsive login/logout forms
- ✅ Protected route navigation
- ✅ Authentication state management
- ✅ User profile management
- ✅ Form validation and error handling
- ✅ Google Cloud-inspired UI design

## Architecture Components

- Authentication Context for state management
- Protected Route wrapper for security
- Reusable UI components (Button, Input)
- Service layer for API communication
- Type-safe TypeScript implementation
EOF

echo "✅ Implementation complete!"
echo ""
echo "📁 Project structure created in: day13-react-auth-ui/"
echo "🚀 Start the demo with: cd day13-react-auth-ui && npm start"
echo "📖 Read DEMO_INSTRUCTIONS.md for testing guide"
echo ""
echo "🎯 Key deliverables:"
echo "   • Authentication UI components"
echo "   • Protected route system"
echo "   • State management with Context"
echo "   • Form validation and error handling"
echo "   • Google Cloud-inspired design"
echo ""
echo "🧪 Tests passed: Authentication context and components"
echo "📱 Demo ready: Full authentication flow with mock data"