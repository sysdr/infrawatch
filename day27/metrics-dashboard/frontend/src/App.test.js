import { render, screen } from '@testing-library/react';
import App from './App';

test('renders metrics dashboard', () => {
  render(<App />);
  const dashboardElement = screen.getByText(/Metrics Dashboard/i);
  expect(dashboardElement).toBeInTheDocument();
});
