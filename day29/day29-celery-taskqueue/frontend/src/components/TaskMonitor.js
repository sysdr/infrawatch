import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function TaskMonitor({ tasks }) {
  const [taskStatuses, setTaskStatuses] = useState({});

  useEffect(() => {
    const updateTaskStatuses = async () => {
      const updates = {};
      
      for (const task of tasks) {
        if (task.task_id && !taskStatuses[task.task_id]?.state?.includes('SUCCESS')) {
          try {
            const response = await axios.get(`${API_BASE}/tasks/${task.task_id}/status`);
            updates[task.task_id] = response.data;
          } catch (error) {
            console.error(`Error fetching task ${task.task_id}:`, error);
          }
        }
      }
      
      if (Object.keys(updates).length > 0) {
        setTaskStatuses(prev => ({ ...prev, ...updates }));
      }
    };

    if (tasks.length > 0) {
      updateTaskStatuses();
      const interval = setInterval(updateTaskStatuses, 2000);
      return () => clearInterval(interval);
    }
  }, [tasks, taskStatuses]);

  const getTaskStatusClass = (state) => {
    switch (state) {
      case 'SUCCESS': return 'success';
      case 'FAILURE': return 'error';
      case 'PROGRESS': return 'progress';
      default: return 'pending';
    }
  };

  const getProgressPercentage = (taskStatus) => {
    if (taskStatus?.state === 'PROGRESS' && taskStatus?.progress) {
      const { processed, total, step } = taskStatus.progress;
      if (processed !== undefined && total !== undefined) {
        return (processed / total) * 100;
      }
      if (step !== undefined && taskStatus.progress.total) {
        return (step / taskStatus.progress.total) * 100;
      }
    }
    return taskStatus?.state === 'SUCCESS' ? 100 : 0;
  };

  return (
    <div>
      <h3>📊 Task Monitor</h3>
      
      <div className="task-list">
        {tasks.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            No tasks executed yet. Click buttons above to start tasks.
          </p>
        ) : (
          tasks.map((task, index) => {
            const taskStatus = taskStatuses[task.task_id];
            const state = taskStatus?.state || 'PENDING';
            const progress = getProgressPercentage(taskStatus);
            
            return (
              <div key={`${task.task_id}-${index}`} className={`task-item ${getTaskStatusClass(state)}`}>
                <div className="task-header">
                  <div>
                    <strong>{task.type || 'Unknown'}</strong>
                    <div className="task-id">ID: {task.task_id}</div>
                  </div>
                  <span className={`task-status ${getTaskStatusClass(state)}`}>
                    {state}
                  </span>
                </div>
                
                {state === 'PROGRESS' && (
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                )}
                
                {taskStatus?.progress?.message && (
                  <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '5px' }}>
                    {taskStatus.progress.message}
                  </div>
                )}
                
                <div style={{ fontSize: '0.8rem', color: '#999', marginTop: '8px' }}>
                  Queue: {task.queue} • Created: {new Date(task.created_at).toLocaleTimeString()}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default TaskMonitor;
