import React from 'react';
import { Clock, CheckCircle, XCircle, Play, Pause } from 'lucide-react';
import './TaskQueue.css';

const TaskQueue = ({ queues = {}, tasks = [], onTaskAction }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="status-icon completed" />;
      case 'running': return <Play className="status-icon running" />;
      case 'failed': return <XCircle className="status-icon failed" />;
      default: return <Clock className="status-icon pending" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#22c55e';
      case 'running': return '#3b82f6';
      case 'failed': return '#ef4444';
      default: return '#f59e0b';
    }
  };

  return (
    <div className="task-queue">
      <h2>Task Queues</h2>
      
      {/* Queue Stats */}
      <div className="queue-stats">
        {Object.entries(queues).map(([queueName, stats]) => (
          <div key={queueName} className="queue-card">
            <h3>{queueName}</h3>
            <div className="queue-metrics">
              <div className="metric">
                <span className="metric-value">{stats.pending}</span>
                <span className="metric-label">Pending</span>
              </div>
              <div className="metric">
                <span className="metric-value">{stats.running}</span>
                <span className="metric-label">Running</span>
              </div>
              <div className="metric">
                <span className="metric-value">{stats.completed}</span>
                <span className="metric-label">Completed</span>
              </div>
              <div className="metric">
                <span className="metric-value">{stats.failed}</span>
                <span className="metric-label">Failed</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Task List */}
      <div className="task-list">
        <h3>Recent Tasks</h3>
        <div className="task-table">
          <div className="task-header">
            <span>Status</span>
            <span>Task Name</span>
            <span>Queue</span>
            <span>Progress</span>
            <span>Worker</span>
            <span>Actions</span>
          </div>
          
          {tasks.slice(0, 10).map(task => (
            <div key={task.id} className="task-row">
              <div className="task-status">
                {getStatusIcon(task.status)}
                <span className="status-text">{task.status}</span>
              </div>
              
              <div className="task-name">{task.name}</div>
              
              <div className="task-queue">
                <span className="queue-badge">{task.queue}</span>
              </div>
              
              <div className="task-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${task.progress}%`,
                      backgroundColor: getStatusColor(task.status)
                    }}
                  />
                </div>
                <span className="progress-text">{task.progress}%</span>
              </div>
              
              <div className="task-worker">{task.worker}</div>
              
              <div className="task-actions">
                {task.status === 'failed' && (
                  <button 
                    className="action-btn retry"
                    onClick={() => onTaskAction && onTaskAction(task.id, 'retry')}
                  >
                    Retry
                  </button>
                )}
                {task.status === 'running' && (
                  <button 
                    className="action-btn cancel"
                    onClick={() => onTaskAction && onTaskAction(task.id, 'cancel')}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TaskQueue;
