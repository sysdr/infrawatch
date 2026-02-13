import React, { useState } from 'react';
import KPIDashboard from './components/KPIDashboard';
import TrendAnalysis from './components/TrendAnalysis';
import Forecasting from './components/Forecasting';
import Comparison from './components/Comparison';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  return (
    <div className="app">
      <header className="header">
        <h1>Business Intelligence Dashboard</h1>
        <p>Real-time KPIs, Trend Analysis, Forecasting</p>
      </header>
      <div className="container">
        <div className="tabs">
          <button className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>KPI Dashboard</button>
          <button className={`tab ${activeTab === 'trends' ? 'active' : ''}`} onClick={() => setActiveTab('trends')}>Trend Analysis</button>
          <button className={`tab ${activeTab === 'forecast' ? 'active' : ''}`} onClick={() => setActiveTab('forecast')}>Forecasting</button>
          <button className={`tab ${activeTab === 'compare' ? 'active' : ''}`} onClick={() => setActiveTab('compare')}>Comparative Analysis</button>
        </div>
        {activeTab === 'dashboard' && <KPIDashboard />}
        {activeTab === 'trends' && <TrendAnalysis />}
        {activeTab === 'forecast' && <Forecasting />}
        {activeTab === 'compare' && <Comparison />}
      </div>
    </div>
  );
}

export default App;
