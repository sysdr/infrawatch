import React, { useState } from 'react';
import { Play, Pause, RotateCcw, Trash2, Settings } from 'lucide-react';
import './TaskControls.css';

const TaskControls = ({ onTaskAction }) => {
  const [selectedQueue, setSelectedQueue] = useState('default');
  const [actionHistory, setActionHistory] = useState([]);

  const queues = ['default', 'priority', 'batch'];

  const handleQueueAction = async (action) => {
    try {
      const response = await fetch(`http://localhost:8000/api/queues/${selectedQueue}/${action}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        const newAction = {
          timestamp: new Date().toISOString(),
          queue: selectedQueue,
          action: action,
          status: 'success'
        };
        setActionHistory(prev => [newAction, ...prev.slice(0, 9)]);
      }
    } catch (error) {
      console.error(`Failed to ${action} queue:`, error);
      const newAction = {
        timestamp: new Date().toISOString(),
        queue: selectedQueue,
        action: action,
        status: 'error'
      };
      setActionHistory(prev => [newAction, ...prev.slice(0, 9)]);
    }
  };

  const ControlButton = ({ icon: Icon, label, onClick, variant = 'primary' }) => (
    <button className={`control-btn ${variant}`} onClick={onClick}>
      <Icon className="btn-icon" />
      <span>{label}</span>
    </button>
  );

  return (
    <div className="task-controls">
      <h2>Queue Controls</h2>
      
      <div className="control-section">
        <div className="queue-selector">
          <label>Select Queue:</label>
          <select value={selectedQueue} onChange={(e) => setSelectedQueue(e.target.value)}>
            {queues.map(queue => (
              <option key={queue} value={queue}>{queue}</option>
            ))}
          </select>
        </div>

        <div className="control-buttons">
          <ControlButton
            icon={Play}
            label="Start"
            onClick={() => handleQueueAction('start')}
            variant="success"
          />
          <ControlButton
            icon={Pause}
            label="Pause"
            onClick={() => handleQueueAction('pause')}
            variant="warning"
          />
          <ControlButton
            icon={RotateCcw}
            label="Restart"
            onClick={() => handleQueueAction('restart')}
            variant="primary"
          />
          <ControlButton
            icon={Trash2}
            label="Clear"
            onClick={() => handleQueueAction('clear')}
            variant="danger"
          />
          <ControlButton
            icon={Settings}
            label="Configure"
            onClick={() => handleQueueAction('configure')}
            variant="secondary"
          />
        </div>
      </div>

      <div className="action-history">
        <h3>Recent Actions</h3>
        <div className="history-list">
          {actionHistory.length === 0 ? (
            <div className="no-history">No recent actions</div>
          ) : (
            actionHistory.map((action, index) => (
              <div key={index} className={`history-item ${action.status}`}>
                <div className="action-info">
                  <span className="action-queue">{action.queue}</span>
                  <span className="action-name">{action.action}</span>
                </div>
                <div className="action-meta">
                  <span className={`action-status ${action.status}`}>
                    {action.status}
                  </span>
                  <span className="action-time">
                    {new Date(action.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskControls;
