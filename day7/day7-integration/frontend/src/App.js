import React, { useState, useEffect } from 'react';
import HealthDashboard from './components/HealthDashboard';
import HelloWorld from './components/HelloWorld';
import ApiTester from './components/ApiTester';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('health');

  return (
    <div className="App">
      <header className="App-header">
        <h1>Day 7: End-to-End Integration Demo</h1>
        <nav className="tab-navigation">
          <button 
            className={activeTab === 'health' ? 'active' : ''}
            onClick={() => setActiveTab('health')}
          >
            Health Dashboard
          </button>
          <button 
            className={activeTab === 'hello' ? 'active' : ''}
            onClick={() => setActiveTab('hello')}
          >
            Hello World
          </button>
          <button 
            className={activeTab === 'api' ? 'active' : ''}
            onClick={() => setActiveTab('api')}
          >
            API Tester
          </button>
        </nav>
      </header>

      <main className="App-main">
        {activeTab === 'health' && <HealthDashboard />}
        {activeTab === 'hello' && <HelloWorld />}
        {activeTab === 'api' && <ApiTester />}
      </main>
    </div>
  );
}

export default App;
