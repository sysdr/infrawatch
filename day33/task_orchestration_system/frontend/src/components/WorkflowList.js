import React from 'react';

const WorkflowList = ({ workflows, onSelectWorkflow, onExecuteWorkflow }) => {
  return (
    <div>
      <div className="wp-card">
        <div className="wp-card-header">
          <h2>All Workflows</h2>
        </div>
        <div className="wp-card-body">
          {workflows.length === 0 ? (
            <p>No workflows available. Create some workflows from the Dashboard.</p>
          ) : (
            <ul className="workflow-list">
              {workflows.map(workflow => (
                <li key={workflow.id} className="workflow-item">
                  <div>
                    <strong>{workflow.name}</strong>
                    <br />
                    <span className={`status-badge status-${workflow.status}`}>
                      {workflow.status}
                    </span>
                    <small style={{ marginLeft: '10px', color: '#666' }}>
                      {workflow.tasks ? workflow.tasks.length : 0} tasks
                    </small>
                    {workflow.started_at && (
                      <small style={{ marginLeft: '10px', color: '#666' }}>
                        Started: {new Date(workflow.started_at).toLocaleTimeString()}
                      </small>
                    )}
                  </div>
                  <div>
                    <button 
                      className="wp-button secondary"
                      onClick={() => onSelectWorkflow(workflow)}
                    >
                      👁️ View Details
                    </button>
                    {workflow.status === 'pending' && (
                      <button 
                        className="wp-button"
                        onClick={() => onExecuteWorkflow(workflow.id)}
                      >
                        ▶️ Execute
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkflowList;
