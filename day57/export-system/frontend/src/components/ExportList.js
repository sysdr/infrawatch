import React from 'react';

const ExportList = ({ exports, onDownload }) => {
  const getStatusColor = (status) => {
    const colors = {
      pending: 'status-pending',
      processing: 'status-processing',
      completed: 'status-completed',
      failed: 'status-failed'
    };
    return colors[status] || 'status-pending';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    return mb >= 1 ? `${mb.toFixed(2)} MB` : `${kb.toFixed(2)} KB`;
  };

  if (exports.length === 0) {
    return (
      <div className="card">
        <h2>📋 Export Jobs</h2>
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <p>No exports yet. Create your first export above!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>📋 Export Jobs ({exports.length})</h2>
      
      {exports.map((exp) => (
        <div key={exp.job_id} className="export-item">
          <div className="export-header">
            <span className="export-id">{exp.job_id}</span>
            <span className={`status-badge ${getStatusColor(exp.status)}`}>
              {exp.status}
            </span>
          </div>

          <div className="export-details">
            <div className="detail-item">
              <span className="detail-label">Format</span>
              <span className="detail-value">{exp.export_format.toUpperCase()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Records</span>
              <span className="detail-value">
                {exp.processed_records} / {exp.total_records}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Created</span>
              <span className="detail-value">{formatDate(exp.created_at)}</span>
            </div>
          </div>

          {exp.status === 'processing' && (
            <div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${exp.progress_percent}%` }}
                ></div>
              </div>
              <p style={{ textAlign: 'center', color: '#667eea', fontWeight: 600 }}>
                {exp.progress_percent}% Complete
              </p>
            </div>
          )}

          {exp.status === 'completed' && (
            <div style={{ marginTop: '1rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => onDownload(exp.job_id)}
              >
                ⬇️ Download Export
              </button>
              <span style={{ marginLeft: '1rem', color: '#718096' }}>
                Completed: {formatDate(exp.completed_at)}
              </span>
            </div>
          )}

          {exp.status === 'failed' && exp.error_message && (
            <div style={{ marginTop: '1rem', color: '#e53e3e', fontSize: '0.9rem' }}>
              ❌ Error: {exp.error_message}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ExportList;
