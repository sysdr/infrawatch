import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { mockApiResponse, createMockLogEvents } from './setupTests';

// Ensure fetch is mocked
global.fetch = jest.fn();

beforeEach(() => {
  global.fetch = jest.fn();
  fetch.mockClear();
});

// Mock fetch globally for these tests
beforeEach(() => {
  fetch.mockClear();
});

describe('App Component', () => {

  test('renders log processing system title', async () => {
  mockApiResponse([]); // Mock empty logs response
  render(<App />);
  
  // Wait for loading to complete and title to appear
  await waitFor(() => {
    expect(screen.getByText('Log Processing System')).toBeInTheDocument();
  });
    expect(screen.getByText(/Distributed Systems Testing Framework/)).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    mockApiResponse([], 200);
    render(<App />);
    
    expect(screen.getByText('Loading logs...')).toBeInTheDocument();
  });

  test('fetches and displays logs on mount', async () => {
    const mockLogs = createMockLogEvents(2);
    mockApiResponse(mockLogs);
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Test log message 1')).toBeInTheDocument();
      expect(screen.getByText('Test log message 2')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Recent Log Events (2)')).toBeInTheDocument();
  });

  test('handles log creation successfully', async () => {
    const user = userEvent.setup();
    const mockLogs = [];
    const newLog = {
      id: 3,
      message: 'New test log',
      level: 'WARNING',
      timestamp: new Date().toISOString(),
      source: 'test-app',
      metadata: null,
    };

    // Mock initial empty logs fetch
    mockApiResponse(mockLogs);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Recent Log Events (0)')).toBeInTheDocument();
    });

    // Mock successful log creation
    mockApiResponse(newLog, 201);

    // Fill out the form
    const messageInput = screen.getByLabelText(/message/i);
    const levelSelect = screen.getByLabelText(/level/i);
    const sourceInput = screen.getByLabelText(/source/i);
    const submitButton = screen.getByRole('button', { name: /create log/i });

    await user.type(messageInput, 'New test log');
    await user.selectOptions(levelSelect, 'WARNING');
    await user.type(sourceInput, 'test-app');
    await user.click(submitButton);

    // Verify the form submission
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/logs'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: 'New test log',
            level: 'WARNING',
            source: 'test-app',
          }),
        })
      );
    });
  });

  test('validates required message field', async () => {
    const user = userEvent.setup();
    
    // Mock empty logs response
    mockApiResponse([]);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Recent Log Events (0)')).toBeInTheDocument();
    });

    // Try to submit without message
    const submitButton = screen.getByRole('button', { name: /create log/i });
    
    // Mock window.alert
    window.alert = jest.fn();
    
    await user.click(submitButton);

    expect(window.alert).toHaveBeenCalledWith('Message is required');
  });

  test('handles API error gracefully', async () => {
    // Mock fetch to reject
    fetch.mockRejectedValueOnce(new Error('Network error'));
    
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/)).toBeInTheDocument();
    });
  });

  test('displays log levels with correct styling', async () => {
    const mockLogs = [
      {
        id: 1,
        message: 'Debug message',
        level: 'DEBUG',
        timestamp: new Date().toISOString(),
        source: 'app',
        metadata: null,
      },
      {
        id: 2,
        message: 'Error message',
        level: 'ERROR',
        timestamp: new Date().toISOString(),
        source: 'app',
        metadata: null,
      },
    ];

    mockApiResponse(mockLogs);
    render(<App />);

    await waitFor(() => {
      const debugLevel = screen.getByText('DEBUG');
      const errorLevel = screen.getByText('ERROR');
      
      expect(debugLevel).toBeInTheDocument();
      expect(errorLevel).toBeInTheDocument();
      
      // Check that levels have styling applied
      expect(debugLevel).toHaveStyle('background-color: #6c757d');
      expect(errorLevel).toHaveStyle('background-color: #dc3545');
    });
  });

  test('resets form after successful submission', async () => {
    const user = userEvent.setup();
    
    // Mock empty logs response
    mockApiResponse([]);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Recent Log Events (0)')).toBeInTheDocument();
    });

    // Mock successful creation
    mockApiResponse({
      id: 1,
      message: 'Test message',
      level: 'INFO',
      timestamp: new Date().toISOString(),
      source: 'test',
      metadata: null,
    }, 201);

    // Fill and submit form
    const messageInput = screen.getByLabelText(/message/i);
    const sourceInput = screen.getByLabelText(/source/i);
    
    await user.type(messageInput, 'Test message');
    await user.type(sourceInput, 'test');
    
    // Mock alert
    window.alert = jest.fn();
    
    await user.click(screen.getByRole('button', { name: /create log/i }));

    // Wait for form reset
    await waitFor(() => {
      expect(messageInput.value).toBe('');
      expect(sourceInput.value).toBe('');
    });
    
    expect(window.alert).toHaveBeenCalledWith('Log created successfully');
  });
});
