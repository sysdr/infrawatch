import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import AlertList from './components/AlertList';
import AlertDetail from './components/AlertDetail';
import AlertStats from './components/AlertStats';
import { AlertProvider } from './services/AlertContext';
import './styles/App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <AlertProvider>
      <Router>
        <div className="app">
          <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
          <div className="app-body">
            <Sidebar isOpen={sidebarOpen} />
            <main className={`main-content ${!sidebarOpen ? 'sidebar-closed' : ''}`}>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/alerts" element={<AlertList />} />
                <Route path="/alerts/:id" element={<AlertDetail />} />
                <Route path="/stats" element={<AlertStats />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </AlertProvider>
  );
}

export default App;
