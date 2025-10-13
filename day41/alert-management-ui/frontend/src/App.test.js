import { render, screen } from '@testing-library/react';
import App from './App';

test('renders alert management text', () => {
  render(<App />);
  const linkElement = screen.getByText(/Alert Management/i);
  expect(linkElement).toBeInTheDocument();
});
