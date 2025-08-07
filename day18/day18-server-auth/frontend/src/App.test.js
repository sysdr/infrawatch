import { render, screen } from '@testing-library/react';
import App from './App';

test('renders server auth app', () => {
  render(<App />);
  const dashboardElement = screen.getByText(/Server Auth/i);
  expect(dashboardElement).toBeInTheDocument();
});
