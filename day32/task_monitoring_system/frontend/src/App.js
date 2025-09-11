import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import TaskList from './components/TaskList';
import WorkerStatus from './components/WorkerStatus';
import MetricsChart from './components/MetricsChart';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import io from 'socket.io-client';

function App() {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io('ws://localhost:8000', {
      path: '/ws/monitoring'
    });
    
    // Use WebSocket API instead
    const ws = new WebSocket('ws://localhost:8000/ws/monitoring');
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    setSocket(ws);
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>Task Monitoring System</h1>
            <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
          </div>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/tasks">Tasks</Link>
            <Link to="/workers">Workers</Link>
            <Link to="/metrics">Metrics</Link>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard socket={socket} />} />
            <Route path="/tasks" element={<TaskList />} />
            <Route path="/workers" element={<WorkerStatus />} />
            <Route path="/metrics" element={<MetricsChart socket={socket} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
