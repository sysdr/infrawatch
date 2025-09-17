import React, { useState, useEffect } from 'react';
import TaskQueue from '../TaskQueue/TaskQueue';
import TaskControls from '../TaskControls/TaskControls';
import TaskHistory from '../TaskHistory/TaskHistory';
import Metrics from '../Metrics/Metrics';
import { Play, Pause, RefreshCw, Activity } from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [queues, setQueues] = useState({});
  const [socket, setSocket] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Initialize WebSocket connection with retry logic
    let ws = null;
    let reconnectTimeout = null;
    
    const connectWebSocket = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          setSocket(ws);
          // Clear any pending reconnection
          if (reconnectTimeout) {
            clearTimeout(reconnectTimeout);
            reconnectTimeout = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'metrics_update') {
              setMetrics(prev => ({ ...prev, ...data.metrics }));
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected, attempting to reconnect...');
          setSocket(null);
          // Reconnect after 3 seconds
          reconnectTimeout = setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        // Retry connection after 5 seconds
        reconnectTimeout = setTimeout(connectWebSocket, 5000);
      }
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        ws.close();
      }
    };
  }, []);

  useEffect(() => {
    fetchTasks();
    fetchQueues();
    fetchMetrics();
    
    const interval = setInterval(() => {
      fetchTasks();
      fetchMetrics();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/tasks');
      const data = await response.json();
      setTasks(data.tasks);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  const fetchQueues = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/queues');
      const data = await response.json();
      setQueues(data.queues);
    } catch (error) {
      console.error('Failed to fetch queues:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const handleTaskAction = async (taskId, action) => {
    try {
      const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/${action}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        fetchTasks(); // Refresh tasks
      }
    } catch (error) {
      console.error(`Failed to ${action} task:`, error);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>
            <Activity className="header-icon" />
            Task Management Dashboard
          </h1>
          <div className="header-stats">
            <div className="stat">
              <span className="stat-value">{tasks.filter(t => t.status === 'running').length}</span>
              <span className="stat-label">Running</span>
            </div>
            <div className="stat">
              <span className="stat-value">{tasks.filter(t => t.status === 'pending').length}</span>
              <span className="stat-label">Pending</span>
            </div>
            <div className="stat">
              <span className="stat-value">{metrics.throughput?.current || 0}</span>
              <span className="stat-label">Throughput/min</span>
            </div>
          </div>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`nav-button ${activeTab === 'queue' ? 'active' : ''}`}
          onClick={() => setActiveTab('queue')}
        >
          Queue
        </button>
        <button 
          className={`nav-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
        <button 
          className={`nav-button ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Metrics
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-grid">
            <Metrics metrics={metrics} />
            <TaskQueue queues={queues} />
            <TaskControls onTaskAction={handleTaskAction} />
          </div>
        )}
        
        {activeTab === 'queue' && (
          <TaskQueue queues={queues} tasks={tasks} onTaskAction={handleTaskAction} />
        )}
        
        {activeTab === 'history' && (
          <TaskHistory tasks={tasks} />
        )}
        
        {activeTab === 'metrics' && (
          <Metrics metrics={metrics} detailed={true} />
        )}
      </main>
    </div>
  );
};

export default Dashboard;
