import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from './components/Dashboard/Dashboard';

// Mock WebSocket
global.WebSocket = class {
  constructor() {}
  close() {}
  onopen = null;
  onmessage = null;
  onclose = null;
  onerror = null;
};

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({
      tasks: [],
      queues: {},
      throughput: { current: 0 },
      latency: { p50: 0 },
      errors: { rate: 0 },
      workers: { active: 0 }
    }),
  }),
);

test('renders dashboard header', () => {
  render(<Dashboard />);
  const linkElement = screen.getByText(/Task Management Dashboard/i);
  expect(linkElement).toBeInTheDocument();
});
