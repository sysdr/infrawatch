import React, { useState, useEffect } from 'react';
import axios from 'axios';

const WorkflowDetail = ({ workflow, onBack, onExecute }) => {
  const [workflowStatus, setWorkflowStatus] = useState(workflow);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/v1/workflows/${workflow.id}/status`);
        setWorkflowStatus(response.data);
      } catch (error) {
        console.error('Error fetching workflow status:', error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [workflow.id]);

  const getProgressPercentage = () => {
    if (!workflowStatus.tasks) return 0;
    const completedTasks = workflowStatus.tasks.filter(t => t.status === 'completed').length;
    return Math.round((completedTasks / workflowStatus.tasks.length) * 100);
  };

  const getTaskIcon = (status) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'ready': return '🔄';
      case 'running': return '▶️';
      case 'completed': return '✅';
      case 'failed': return '❌';
      case 'skipped': return '⏭️';
      default: return '❓';
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <button className="wp-button secondary" onClick={onBack}>
          ← Back to Workflows
        </button>
      </div>

      <div className="wp-card">
        <div className="wp-card-header">
          <h2>{workflowStatus.name}</h2>
          <span className={`status-badge status-${workflowStatus.status}`}>
            {workflowStatus.status}
          </span>
        </div>
        <div className="wp-card-body">
          <div style={{ marginBottom: '20px' }}>
            <strong>Progress: {getProgressPercentage()}%</strong>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <strong>Workflow ID:</strong> {workflowStatus.id}
            <br />
            <strong>Created:</strong> {new Date(workflowStatus.created_at).toLocaleString()}
            {workflowStatus.started_at && (
              <>
                <br />
                <strong>Started:</strong> {new Date(workflowStatus.started_at).toLocaleString()}
              </>
            )}
            {workflowStatus.completed_at && (
              <>
                <br />
                <strong>Completed:</strong> {new Date(workflowStatus.completed_at).toLocaleString()}
              </>
            )}
          </div>

          {workflowStatus.status === 'pending' && (
            <button 
              className="wp-button"
              onClick={() => onExecute(workflowStatus.id)}
            >
              ▶️ Execute Workflow
            </button>
          )}
        </div>
      </div>

      <div className="wp-card">
        <div className="wp-card-header">
          <h2>Tasks ({workflowStatus.tasks ? workflowStatus.tasks.length : 0})</h2>
        </div>
        <div className="wp-card-body">
          {workflowStatus.tasks && workflowStatus.tasks.length > 0 ? (
            <div className="task-grid">
              {workflowStatus.tasks.map(task => (
                <div key={task.id} className="task-item">
                  <div style={{ marginBottom: '10px' }}>
                    <span style={{ fontSize: '20px' }}>{getTaskIcon(task.status)}</span>
                    <strong style={{ marginLeft: '10px' }}>{task.name}</strong>
                    <span 
                      className={`status-badge status-${task.status}`}
                      style={{ float: 'right' }}
                    >
                      {task.status}
                    </span>
                  </div>
                  
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
                    ID: {task.id}
                    {task.retry_count > 0 && (
                      <span style={{ marginLeft: '10px' }}>
                        Retries: {task.retry_count}
                      </span>
                    )}
                  </div>

                  {task.started_at && (
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      Started: {new Date(task.started_at).toLocaleTimeString()}
                    </div>
                  )}

                  {task.completed_at && (
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      Completed: {new Date(task.completed_at).toLocaleTimeString()}
                    </div>
                  )}

                  {task.error && (
                    <div style={{ 
                      backgroundColor: '#f8d7da', 
                      color: '#721c24', 
                      padding: '8px', 
                      borderRadius: '3px', 
                      fontSize: '12px',
                      marginTop: '10px'
                    }}>
                      Error: {task.error}
                    </div>
                  )}

                  {task.result && (
                    <div className="task-result">
                      <strong>Result:</strong>
                      <pre style={{ margin: '5px 0 0 0', whiteSpace: 'pre-wrap' }}>
                        {typeof task.result === 'object' 
                          ? JSON.stringify(task.result, null, 2)
                          : task.result
                        }
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p>No tasks available for this workflow.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkflowDetail;
