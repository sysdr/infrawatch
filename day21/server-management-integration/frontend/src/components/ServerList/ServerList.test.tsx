import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ServerList } from './ServerList';
import * as api from '../../services/api';

// Mock the API
jest.mock('../../services/api');
const mockApi = api as jest.Mocked<typeof api>;

// Mock WebSocket
jest.mock('../../hooks/useWebSocket', () => ({
  useWebSocket: () => ({ sendMessage: jest.fn() })
}));

const mockServers = [
  {
    id: 1,
    name: 'Test Server 1',
    status: 'running' as const,
    description: 'Test description',
    ip_address: '192.168.1.100',
    port: 8080,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: 'Test Server 2',
    status: 'stopped' as const,
    description: 'Another test server',
    ip_address: '192.168.1.101',
    port: 8081,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
];

describe('ServerList Component', () => {
  beforeEach(() => {
    // Properly mock the async function
    (mockApi.serverApi.getServers as jest.Mock).mockResolvedValue(mockServers);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders server list', async () => {
    render(<ServerList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Server 1')).toBeInTheDocument();
      expect(screen.getByText('Test Server 2')).toBeInTheDocument();
    });
  });

  test('shows loading state initially', () => {
    render(<ServerList />);
    expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
  });

  test('opens create modal when create button is clicked', async () => {
    render(<ServerList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Server 1')).toBeInTheDocument();
    });

    const createButton = screen.getByRole('button', { name: /create server/i });
    fireEvent.click(createButton);

    expect(screen.getByText('Create New Server')).toBeInTheDocument();
  });

  test('displays empty state when no servers', async () => {
    (mockApi.serverApi.getServers as jest.Mock).mockResolvedValue([]);
    
    render(<ServerList />);
    
    await waitFor(() => {
      expect(screen.getByText('No servers found')).toBeInTheDocument();
    });
  });
});
