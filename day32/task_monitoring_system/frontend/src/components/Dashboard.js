import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Users, Clock, AlertTriangle } from 'lucide-react';
import './Dashboard.css';

const Dashboard = ({ socket }) => {
  const [metrics, setMetrics] = useState({
    tasks: { total: 0, queued: 0, processing: 0, completed: 0, failed: 0 },
    workers: { total: 0, healthy: 0, unhealthy: 0 },
    performance: { avg_execution_time: 0, throughput_per_hour: 0 },
    system: { cpu_usage: 0, memory_usage: 0, disk_usage: 0 }
  });
  
  const [recentTasks, setRecentTasks] = useState([]);

  useEffect(() => {
    // Fetch initial metrics
    fetchMetrics();
    
    // Set up WebSocket listener for real-time updates
    if (socket) {
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setMetrics(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    }
    
    // Fallback polling
    const interval = setInterval(fetchMetrics, 5000);
    
    return () => clearInterval(interval);
  }, [socket]);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/monitoring/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const fetchRecentTasks = async () => {
    try {
      const response = await axios.get('/api/tasks?limit=10');
      setRecentTasks(response.data);
    } catch (error) {
      console.error('Error fetching recent tasks:', error);
    }
  };

  useEffect(() => {
    fetchRecentTasks();
  }, []);

  const createTask = async () => {
    try {
      const taskData = {
        name: `Demo Task ${Date.now()}`,
        payload: { demo: true, timestamp: Date.now() },
        queue_name: 'default',
        priority: 1
      };
      
      await axios.post('/api/tasks/', taskData);
      fetchRecentTasks();
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>System Overview</h2>
        <button onClick={createTask} className="create-task-btn">
          Create Demo Task
        </button>
      </div>
      
      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <Activity />
          </div>
          <div className="metric-content">
            <h3>Active Tasks</h3>
            <div className="metric-value">{metrics.tasks.processing}</div>
            <div className="metric-subtitle">
              {metrics.tasks.queued} queued, {metrics.tasks.completed} completed
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">
            <Users />
          </div>
          <div className="metric-content">
            <h3>Workers</h3>
            <div className="metric-value">{metrics.workers.healthy}</div>
            <div className="metric-subtitle">
              {metrics.workers.unhealthy} unhealthy
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">
            <Clock />
          </div>
          <div className="metric-content">
            <h3>Avg Execution Time</h3>
            <div className="metric-value">{metrics.performance.avg_execution_time}s</div>
            <div className="metric-subtitle">
              {metrics.performance.throughput_per_hour}/hr throughput
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">
            <AlertTriangle />
          </div>
          <div className="metric-content">
            <h3>Failed Tasks</h3>
            <div className="metric-value">{metrics.tasks.failed}</div>
            <div className="metric-subtitle">
              Last 24 hours
            </div>
          </div>
        </div>
      </div>
      
      {/* System Health */}
      <div className="system-health">
        <h3>System Health</h3>
        <div className="health-metrics">
          <div className="health-item">
            <span>CPU Usage</span>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${metrics.system.cpu_usage}%` }}
              />
            </div>
            <span>{metrics.system.cpu_usage}%</span>
          </div>
          
          <div className="health-item">
            <span>Memory Usage</span>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${metrics.system.memory_usage}%` }}
              />
            </div>
            <span>{metrics.system.memory_usage}%</span>
          </div>
          
          <div className="health-item">
            <span>Disk Usage</span>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${metrics.system.disk_usage}%` }}
              />
            </div>
            <span>{metrics.system.disk_usage}%</span>
          </div>
        </div>
      </div>
      
      {/* Recent Tasks */}
      <div className="recent-tasks">
        <h3>Recent Tasks</h3>
        <div className="task-list">
          {recentTasks.map(task => (
            <div key={task.id} className={`task-item ${task.status}`}>
              <div className="task-info">
                <strong>{task.name}</strong>
                <span className="task-id">#{task.id}</span>
              </div>
              <div className="task-status">
                <span className={`status-badge ${task.status}`}>
                  {task.status}
                </span>
                <span className="task-time">
                  {new Date(task.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
