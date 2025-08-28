import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';
import './App.css';

// Components
import Dashboard from './pages/Dashboard';
import Metrics from './pages/Metrics';
import Statistics from './pages/Statistics';
import Rollups from './pages/Rollups';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

// API Configuration
axios.defaults.baseURL = 'http://localhost:8000/api/v1';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [systemStats, setSystemStats] = useState({});

  useEffect(() => {
    // Check backend connection
    checkConnection();
    
    // Setup periodic health checks
    const healthInterval = setInterval(checkConnection, 30000);
    
    return () => clearInterval(healthInterval);
  }, []);

  const checkConnection = async () => {
    try {
      const response = await axios.get('/health');
      if (response.data.status === 'healthy') {
        setIsConnected(true);
        if (!systemStats.lastConnected) {
          toast.success('Connected to Metrics Aggregation System');
        }
        setSystemStats(prev => ({
          ...prev,
          lastConnected: new Date().toISOString(),
          components: response.data.components
        }));
      }
    } catch (error) {
      setIsConnected(false);
      setSystemStats(prev => ({
        ...prev,
        lastError: error.message,
        lastAttempt: new Date().toISOString()
      }));
    }
  };

  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <div className="App min-h-screen bg-gray-50">
        <Toaster position="top-right" />
        
        {/* WordPress-inspired layout */}
        <div className="flex h-screen">
          {/* Sidebar */}
          <div className="w-64 bg-white shadow-lg border-r border-gray-200">
            <Sidebar 
              currentPage={currentPage}
              onPageChange={setCurrentPage}
              isConnected={isConnected}
            />
          </div>
          
          {/* Main content area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header 
              isConnected={isConnected}
              systemStats={systemStats}
              currentPage={currentPage}
            />
            
            {/* Page content */}
            <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
              <Routes>
                <Route path="/" element={
                  <Dashboard 
                    isConnected={isConnected}
                    systemStats={systemStats}
                  />
                } />
                <Route path="/metrics" element={
                  <Metrics isConnected={isConnected} />
                } />
                <Route path="/statistics" element={
                  <Statistics isConnected={isConnected} />
                } />
                <Route path="/rollups" element={
                  <Rollups isConnected={isConnected} />
                } />
              </Routes>
            </main>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
