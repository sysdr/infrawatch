import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function TaskManager({ onTaskCreated }) {
  const [loading, setLoading] = useState({});

  const executeTask = async (taskType, endpoint, payload = {}) => {
    setLoading(prev => ({ ...prev, [taskType]: true }));
    
    try {
      const response = await axios.post(`${API_BASE}${endpoint}`, payload);
      onTaskCreated({
        ...response.data,
        type: taskType,
        created_at: new Date().toISOString()
      });
    } catch (error) {
      console.error(`Error executing ${taskType}:`, error);
    } finally {
      setLoading(prev => ({ ...prev, [taskType]: false }));
    }
  };

  return (
    <div>
      <h3>🎯 Task Manager</h3>
      
      <div className="task-controls">
        <button 
          className="task-button"
          onClick={() => executeTask('metrics', '/tasks/metrics/start')}
          disabled={loading.metrics}
        >
          {loading.metrics ? '⏳' : '📊'} Collect Metrics
        </button>
        
        <button 
          className="task-button secondary"
          onClick={() => executeTask('data-processing', '/tasks/data/process', {
            batch: Array.from({length: 20}, (_, i) => `item_${i}`)
          })}
          disabled={loading['data-processing']}
        >
          {loading['data-processing'] ? '⏳' : '⚙️'} Process Data
        </button>
        
        <button 
          className="task-button"
          onClick={() => executeTask('notification', '/tasks/notification/send', {
            message: 'Test notification from dashboard',
            priority: 'normal'
          })}
          disabled={loading.notification}
        >
          {loading.notification ? '⏳' : '📧'} Send Notification
        </button>
        
        <button 
          className="task-button secondary"
          onClick={() => executeTask('report', '/tasks/report/generate', {
            type: 'system_metrics',
            filters: { period: '24h' }
          })}
          disabled={loading.report}
        >
          {loading.report ? '⏳' : '📋'} Generate Report
        </button>
      </div>
    </div>
  );
}

export default TaskManager;
