import React from 'react';
import { ServerList } from './components/ServerList/ServerList';
import './index.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <ServerList />
      </div>
    </div>
  );
}

export default App;
