import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock fetch globally
global.fetch = jest.fn();

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers that are declared in a test
afterEach(() => {
  server.resetHandlers();
  fetch.mockClear();
});

// Clean up after the tests are finished
afterAll(() => server.close());

// Global test utilities
export const mockApiResponse = (data, status = 200) => {
  fetch.mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
    text: async () => JSON.stringify(data),
  });
};

export const mockApiError = (status = 500, message = 'Server Error') => {
  fetch.mockRejectedValueOnce(new Error(message));
};

export const createMockLogEvent = (overrides = {}) => ({
  id: 1,
  message: 'Test log message',
  level: 'INFO',
  timestamp: new Date().toISOString(),
  source: 'test-app',
  metadata: null,
  ...overrides,
});

export const createMockLogEvents = (count = 5) => {
  return Array.from({ length: count }, (_, index) =>
    createMockLogEvent({
      id: index + 1,
      message: `Test log message ${index + 1}`,
    })
  );
};
