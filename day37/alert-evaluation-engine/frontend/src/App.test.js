import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the components to avoid routing issues in tests
jest.mock('./components/Dashboard', () => {
  return function Dashboard() {
    return <div data-testid="dashboard">Dashboard Component</div>;
  };
});

jest.mock('./components/RulesManager', () => {
  return function RulesManager() {
    return <div data-testid="rules">Rules Manager Component</div>;
  };
});

jest.mock('./components/AlertsView', () => {
  return function AlertsView() {
    return <div data-testid="alerts">Alerts View Component</div>;
  };
});

test('renders app header', () => {
  render(<App />);
  const linkElement = screen.getByText(/Alert Evaluation Engine/i);
  expect(linkElement).toBeInTheDocument();
});

test('renders dashboard by default', () => {
  render(<App />);
  const dashboard = screen.getByTestId('dashboard');
  expect(dashboard).toBeInTheDocument();
});
