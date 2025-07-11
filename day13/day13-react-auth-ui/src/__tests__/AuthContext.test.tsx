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
