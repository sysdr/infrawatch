import React from 'react';

const Dashboard = ({ workflows, metrics, onCreateSample, onExecuteWorkflow, loading }) => {
  const completedWorkflows = workflows.filter(w => w.status === 'completed').length;
  const runningWorkflows = workflows.filter(w => w.status === 'running').length;
  const failedWorkflows = workflows.filter(w => w.status === 'failed').length;

  return (
    <div>
      <div className="wp-card">
        <div className="wp-card-header">
          <h2>System Overview</h2>
        </div>
        <div className="wp-card-body">
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-value">{workflows.length}</span>
              <div className="metric-label">Total Workflows</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{runningWorkflows}</span>
              <div className="metric-label">Running</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{completedWorkflows}</span>
              <div className="metric-label">Completed</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{failedWorkflows}</span>
              <div className="metric-label">Failed</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{metrics.total_tasks || 0}</span>
              <div className="metric-label">Total Tasks</div>
            </div>
            <div className="metric-card">
              <span className="metric-value">{metrics.success_rate || 0}%</span>
              <div className="metric-label">Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      <div className="wp-card">
        <div className="wp-card-header">
          <h2>Quick Actions</h2>
        </div>
        <div className="wp-card-body">
          <p>Create and execute sample workflows to see the orchestration patterns in action:</p>
          <div style={{ marginTop: '15px' }}>
            <button 
              className="wp-button"
              onClick={() => onCreateSample('ecommerce')}
              disabled={loading}
            >
              {loading ? 'Creating...' : '🛒 Create E-Commerce Workflow'}
            </button>
            <button 
              className="wp-button"
              onClick={() => onCreateSample('blog')}
              disabled={loading}
            >
              {loading ? 'Creating...' : '📝 Create Blog Publishing Workflow'}
            </button>
          </div>
        </div>
      </div>

      <div className="wp-card">
        <div className="wp-card-header">
          <h2>Recent Workflows</h2>
        </div>
        <div className="wp-card-body">
          {workflows.length === 0 ? (
            <p>No workflows created yet. Use the quick actions above to get started!</p>
          ) : (
            <ul className="workflow-list">
              {workflows.slice(0, 5).map(workflow => (
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
                  </div>
                  <div>
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

export default Dashboard;
