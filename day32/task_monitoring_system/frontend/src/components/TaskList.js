import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, X, RotateCcw } from 'lucide-react';
import './TaskList.css';

const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter !== 'all') {
        params.status = filter;
      }
      
      const response = await axios.get('/api/tasks/', { params });
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const processTask = async (taskId) => {
    try {
      await axios.post(`/api/tasks/${taskId}/process`, {
        worker_id: `demo-worker-${Date.now()}`
      });
      
      setTimeout(() => fetchTasks(), 1000); // Refresh after processing
    } catch (error) {
      console.error('Error processing task:', error);
    }
  };

  const cancelTask = async (taskId) => {
    try {
      await axios.post(`/api/tasks/${taskId}/cancel`);
      fetchTasks();
    } catch (error) {
      console.error('Error cancelling task:', error);
    }
  };

  const createTestTask = async () => {
    try {
      const taskData = {
        name: `Test Task ${Date.now()}`,
        payload: { test: true, created_at: new Date().toISOString() },
        queue_name: 'default',
        priority: Math.floor(Math.random() * 5) + 1
      };
      
      await axios.post('/api/tasks/', taskData);
      fetchTasks();
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      queued: '#fbbf24',
      processing: '#3b82f6',
      completed: '#10b981',
      failed: '#ef4444',
      retrying: '#f97316',
      cancelled: '#6b7280'
    };
    return colors[status] || '#6b7280';
  };

  const filteredTasks = tasks.filter(task => 
    filter === 'all' || task.status === filter
  );

  return (
    <div className="task-list-container">
      <div className="task-list-header">
        <h2>Task Management</h2>
        <div className="header-actions">
          <button onClick={createTestTask} className="create-btn">
            Create Test Task
          </button>
          <button onClick={fetchTasks} className="refresh-btn">
            <RotateCcw size={16} />
            Refresh
          </button>
        </div>
      </div>
      
      {/* Filters */}
      <div className="filter-bar">
        <div className="filter-buttons">
          {['all', 'queued', 'processing', 'completed', 'failed', 'retrying'].map(status => (
            <button
              key={status}
              className={`filter-btn ${filter === status ? 'active' : ''}`}
              onClick={() => setFilter(status)}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
        
        <div className="task-count">
          {filteredTasks.length} tasks
        </div>
      </div>
      
      {/* Task List */}
      <div className="task-list">
        {loading ? (
          <div className="loading">Loading tasks...</div>
        ) : filteredTasks.length === 0 ? (
          <div className="empty-state">
            <p>No tasks found</p>
            <button onClick={createTestTask} className="create-btn">
              Create Test Task
            </button>
          </div>
        ) : (
          <div className="task-grid">
            {filteredTasks.map(task => (
              <div key={task.id} className="task-card">
                <div className="task-header">
                  <div className="task-title">
                    <h3>{task.name}</h3>
                    <span className="task-id">#{task.id}</span>
                  </div>
                  <div 
                    className="status-indicator"
                    style={{ backgroundColor: getStatusColor(task.status) }}
                  >
                    {task.status}
                  </div>
                </div>
                
                <div className="task-details">
                  <div className="detail-row">
                    <span>Queue:</span>
                    <span>{task.queue_name}</span>
                  </div>
                  
                  <div className="detail-row">
                    <span>Priority:</span>
                    <span>{task.priority}</span>
                  </div>
                  
                  <div className="detail-row">
                    <span>Retries:</span>
                    <span>{task.retry_count}/{task.max_retries}</span>
                  </div>
                  
                  {task.execution_time && (
                    <div className="detail-row">
                      <span>Execution Time:</span>
                      <span>{task.execution_time.toFixed(2)}s</span>
                    </div>
                  )}
                  
                  {task.worker_id && (
                    <div className="detail-row">
                      <span>Worker:</span>
                      <span>{task.worker_id}</span>
                    </div>
                  )}
                  
                  <div className="detail-row">
                    <span>Created:</span>
                    <span>{new Date(task.created_at).toLocaleString()}</span>
                  </div>
                  
                  {task.error_message && (
                    <div className="error-message">
                      <strong>Error:</strong> {task.error_message}
                    </div>
                  )}
                </div>
                
                <div className="task-actions">
                  {task.status === 'queued' && (
                    <button 
                      onClick={() => processTask(task.id)}
                      className="action-btn process"
                    >
                      <Play size={16} />
                      Process
                    </button>
                  )}
                  
                  {['queued', 'processing'].includes(task.status) && (
                    <button 
                      onClick={() => cancelTask(task.id)}
                      className="action-btn cancel"
                    >
                      <X size={16} />
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskList;
