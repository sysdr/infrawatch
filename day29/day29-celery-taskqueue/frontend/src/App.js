import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TaskManager from './components/TaskManager';
import WorkerStats from './components/WorkerStats';
import TaskMonitor from './components/TaskMonitor';
import './App.css';

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [workers, setWorkers] = useState({});
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchData = () => {
      // Fetch worker stats
      axios.get(`${API_BASE}/workers/stats`)
        .then(response => setWorkers(response.data))
        .catch(error => console.error('Error fetching workers:', error));
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const addTask = (task) => {
    setTasks(prev => [task, ...prev].slice(0, 20)); // Keep last 20 tasks
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 Celery Task Queue Dashboard</h1>
        <p>Real-time monitoring and task management</p>
      </header>
      
      <div className="dashboard-grid">
        <div className="card">
          <WorkerStats workers={workers} />
        </div>
        
        <div className="card">
          <TaskManager onTaskCreated={addTask} />
        </div>
        
        <div className="card full-width">
          <TaskMonitor tasks={tasks} />
        </div>
      </div>
    </div>
  );
}

export default App;
