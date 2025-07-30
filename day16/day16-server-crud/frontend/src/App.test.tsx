import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders server management dashboard', () => {
  render(<App />);
  const dashboardElement = screen.getByText(/Server Management Dashboard/i);
  expect(dashboardElement).toBeInTheDocument();
});

test('renders total servers card', () => {
  render(<App />);
  const totalServersElement = screen.getByText(/Total Servers/i);
  expect(totalServersElement).toBeInTheDocument();
});
