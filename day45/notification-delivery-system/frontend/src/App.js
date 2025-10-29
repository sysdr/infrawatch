import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Notifications from './pages/Notifications';
import Tracking from './pages/Tracking';
import Settings from './pages/Settings';
import { Bell, BarChart3, Search, Settings as SettingsIcon } from 'lucide-react';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [realtimeData, setRealtimeData] = useState(null);

  useEffect(() => {
    // WebSocket connection for real-time updates
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      
      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setRealtimeData(data);
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connectWebSocket();
  }, []);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <Bell className="h-8 w-8 text-blue-600 mr-3" />
                <h1 className="text-xl font-semibold text-gray-900">
                  Notification Delivery System
                </h1>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm font-medium">
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              <Link 
                to="/" 
                className="border-b-2 border-transparent hover:border-blue-500 px-1 py-4 text-sm font-medium text-gray-900 hover:text-blue-600 flex items-center space-x-2"
              >
                <BarChart3 className="h-4 w-4" />
                <span>Dashboard</span>
              </Link>
              <Link 
                to="/notifications" 
                className="border-b-2 border-transparent hover:border-blue-500 px-1 py-4 text-sm font-medium text-gray-900 hover:text-blue-600 flex items-center space-x-2"
              >
                <Bell className="h-4 w-4" />
                <span>Notifications</span>
              </Link>
              <Link 
                to="/tracking" 
                className="border-b-2 border-transparent hover:border-blue-500 px-1 py-4 text-sm font-medium text-gray-900 hover:text-blue-600 flex items-center space-x-2"
              >
                <Search className="h-4 w-4" />
                <span>Tracking</span>
              </Link>
              <Link 
                to="/settings" 
                className="border-b-2 border-transparent hover:border-blue-500 px-1 py-4 text-sm font-medium text-gray-900 hover:text-blue-600 flex items-center space-x-2"
              >
                <SettingsIcon className="h-4 w-4" />
                <span>Settings</span>
              </Link>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard realtimeData={realtimeData} />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/tracking" element={<Tracking />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
