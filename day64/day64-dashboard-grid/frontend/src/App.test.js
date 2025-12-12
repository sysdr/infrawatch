import { render, screen, waitFor } from '@testing-library/react';
import App from './App';
import { dashboardAPI, widgetAPI } from './services/api';

// Mock the API services
jest.mock('./services/api', () => ({
  dashboardAPI: {
    getAll: jest.fn(() => Promise.resolve({ data: [] })),
    getById: jest.fn(),
    create: jest.fn(() => Promise.resolve({ data: { id: '1', name: 'My Dashboard', description: 'Test', layout: [] } })),
    update: jest.fn(),
    delete: jest.fn(),
  },
  widgetAPI: {
    getByDashboard: jest.fn(() => Promise.resolve({ data: [] })),
    create: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  },
  templateAPI: {
    getAll: jest.fn(() => Promise.resolve({ data: [] })),
    create: jest.fn(),
    apply: jest.fn(),
  },
}));

test('renders dashboard title', async () => {
  render(<App />);
  await waitFor(() => {
    const titleElement = screen.getByText(/Dashboard Grid System/i);
    expect(titleElement).toBeInTheDocument();
  });
});
