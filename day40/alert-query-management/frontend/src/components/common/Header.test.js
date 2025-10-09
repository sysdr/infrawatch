import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from './Header';

test('renders header with navigation', () => {
  render(
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Header />
    </BrowserRouter>
  );
  
  expect(screen.getByText('🚨 Alert Management')).toBeInTheDocument();
  expect(screen.getByText('Dashboard')).toBeInTheDocument();
  expect(screen.getByText('Search')).toBeInTheDocument();
  expect(screen.getByText('Statistics')).toBeInTheDocument();
});
