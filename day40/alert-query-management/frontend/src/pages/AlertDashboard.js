import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';

const AlertDashboard = () => {
  const [selectedAlerts, setSelectedAlerts] = useState([]);
  
  const { data: alerts, isLoading, refetch } = useQuery(
    'recent-alerts',
    async () => {
      const response = await axios.post('/api/alerts/search', {
        limit: 50,
        sort_by: 'created_at',
        sort_order: 'desc'
      });
      return response.data;
    },
    { refetchInterval: 30000 }
  );

  const { data: stats } = useQuery(
    'alert-stats',
    async () => {
      const response = await axios.get('/api/alerts/statistics');
      return response.data;
    },
    { refetchInterval: 30000 }
  );

  const handleBulkAction = async (action) => {
    if (selectedAlerts.length === 0) return;
    
    const updates = {};
    if (action === 'acknowledge') {
      updates.status = 'acknowledged';
      updates.acknowledged_at = new Date().toISOString();
    } else if (action === 'resolve') {
      updates.status = 'resolved';
      updates.resolved_at = new Date().toISOString();
    }
    
    try {
      await axios.post('/api/alerts/bulk-update', {
        alert_ids: selectedAlerts,
        updates
      });
      setSelectedAlerts([]);
      refetch();
    } catch (error) {
      console.error('Bulk action failed:', error);
    }
  };

  if (isLoading) {
    return <div className="loading">Loading alerts...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Alert Dashboard</h1>
        <p className="page-subtitle">Real-time alert monitoring and management</p>
      </div>

      {stats && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Alert Overview</h2>
          </div>
          <div className="card-body">
            <div style={{display: 'flex', gap: '20px', marginBottom: '20px'}}>
              <div>
                <strong>Total Alerts:</strong> {stats.total_alerts}
              </div>
              <div>
                <strong>Active:</strong> {stats.active_alerts}
              </div>
            </div>
            
            <div style={{display: 'flex', gap: '40px'}}>
              <div>
                <h4>By Status</h4>
                {stats.status_distribution?.map(stat => (
                  <div key={stat.status}>
                    {stat.status}: {stat.count}
                  </div>
                ))}
              </div>
              
              <div>
                <h4>By Severity</h4>
                {stats.severity_distribution?.map(stat => (
                  <div key={stat.severity}>
                    {stat.severity}: {stat.count}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Alerts</h2>
          <div style={{marginLeft: 'auto', display: 'flex', gap: '10px'}}>
            {selectedAlerts.length > 0 && (
              <>
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleBulkAction('acknowledge')}
                >
                  Acknowledge ({selectedAlerts.length})
                </button>
                <button 
                  className="btn btn-success btn-sm"
                  onClick={() => handleBulkAction('resolve')}
                >
                  Resolve ({selectedAlerts.length})
                </button>
              </>
            )}
          </div>
        </div>
        <div className="card-body">
          {alerts?.alerts?.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>
                    <input 
                      type="checkbox"
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedAlerts(alerts.alerts.map(a => a.id));
                        } else {
                          setSelectedAlerts([]);
                        }
                      }}
                    />
                  </th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Severity</th>
                  <th>Source</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {alerts.alerts.map(alert => (
                  <tr key={alert.id}>
                    <td>
                      <input 
                        type="checkbox"
                        checked={selectedAlerts.includes(alert.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedAlerts([...selectedAlerts, alert.id]);
                          } else {
                            setSelectedAlerts(selectedAlerts.filter(id => id !== alert.id));
                          }
                        }}
                      />
                    </td>
                    <td>{alert.title}</td>
                    <td>
                      <span className={`status-badge status-${alert.status}`}>
                        {alert.status}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge severity-${alert.severity}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td>{alert.source}</td>
                    <td>{new Date(alert.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">No alerts found</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertDashboard;
