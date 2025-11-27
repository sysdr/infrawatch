import React, { useState } from 'react';

const ExportForm = ({ onSubmit, loading }) => {
  const [format, setFormat] = useState('csv');
  const [userId, setUserId] = useState('');
  const [notificationType, setNotificationType] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const request = {
      export_format: format,
      user_id: userId ? parseInt(userId) : null,
      notification_type: notificationType || null
    };
    
    onSubmit(request);
  };

  return (
    <div className="card">
      <h2>🚀 Create New Export</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="format">Export Format</label>
          <select
            id="format"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <option value="csv">CSV (Spreadsheet)</option>
            <option value="json">JSON (API Compatible)</option>
            <option value="pdf">PDF (Report)</option>
            <option value="excel">Excel (Advanced)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="userId">User ID (Optional)</label>
          <input
            id="userId"
            type="number"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Filter by user ID"
          />
        </div>

        <div className="form-group">
          <label htmlFor="notificationType">Notification Type (Optional)</label>
          <select
            id="notificationType"
            value={notificationType}
            onChange={(e) => setNotificationType(e.target.value)}
          >
            <option value="">All Types</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="success">Success</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? '⏳ Creating...' : '📥 Create Export'}
        </button>
      </form>
    </div>
  );
};

export default ExportForm;
