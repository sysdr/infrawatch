import React from 'react';
import { RealtimeProvider } from './contexts/RealtimeContext';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <RealtimeProvider>
      <Dashboard />
    </RealtimeProvider>
  );
}

export default App;
