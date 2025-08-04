import { render, screen } from '@testing-library/react';
import App from '../src/App';

test('renders navigation', () => {
  render(<App />);
  const dashboardLink = screen.getByText(/Dashboard/i);
  expect(dashboardLink).toBeInTheDocument();
});

test('renders server validation page', () => {
  render(<App />);
  // Add more specific tests based on your components
});
