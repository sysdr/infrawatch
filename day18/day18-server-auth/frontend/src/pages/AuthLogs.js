import React, { useState, useEffect } from 'react';
import { RefreshCw, Filter } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/auth-logs/');
      setLogs(response.data);
    } catch (error) {
      toast.error('Failed to fetch auth logs');
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filter === 'all') return true;
    return log.status === filter;
  });

  const getActionIcon = (action) => {
    switch (action) {
      case 'connection_test': return '🔌';
      case 'key_rotation': return '🔄';
      case 'expiration_warning': return '⚠️';
      default: return '📋';
    }
  };

  if (loading) return <div className="loading">Loading auth logs...</div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Authentication Logs</h1>
        <p className="page-subtitle">Monitor authentication activities and security events</p>
      </div>

      <div className="content-card">
        <div className="card-header">
          <h2 className="card-title">Security Audit Trail</h2>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <select
              className="form-input"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              style={{ width: 'auto', minWidth: '120px' }}
            >
              <option value="all">All Events</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
              <option value="warning">Warning</option>
            </select>
            <button 
              className="btn btn-secondary"
              onClick={fetchLogs}
              title="Refresh Logs"
            >
              <RefreshCw size={16} />
            </button>
          </div>
        </div>

        <div className="logs-container">
          {filteredLogs.length > 0 ? (
            filteredLogs.map((log) => (
              <div 
                key={log.id} 
                className="log-entry"
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  padding: '16px',
                  borderBottom: '1px solid #e8eaed',
                  gap: '16px'
                }}
              >
                <div style={{ fontSize: '20px', flexShrink: 0 }}>
                  {getActionIcon(log.action)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <h4 style={{ margin: 0, fontSize: '16px', fontWeight: '500' }}>
                      {log.action.replace('_', ' ').toUpperCase()}
                    </h4>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span className={`status-badge status-${log.status}`}>
                        {log.status}
                      </span>
                      <span style={{ fontSize: '12px', color: '#5f6368' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <p style={{ margin: 0, color: '#5f6368' }}>
                    {log.details}
                  </p>
                  {(log.server_id || log.ssh_key_id) && (
                    <div style={{ marginTop: '8px', fontSize: '12px', color: '#5f6368' }}>
                      {log.server_id && <span>Server ID: {log.server_id}</span>}
                      {log.server_id && log.ssh_key_id && <span> • </span>}
                      {log.ssh_key_id && <span>SSH Key ID: {log.ssh_key_id}</span>}
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#5f6368' }}>
              <Filter size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
              <p>No logs found for the selected filter</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthLogs;
