import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Key, Server, Activity, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('/dashboard/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;

  const chartData = [
    { name: 'SSH Keys', active: stats?.active_keys || 0, total: stats?.total_keys || 0 },
    { name: 'Servers', active: stats?.connected_servers || 0, total: stats?.total_servers || 0 }
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Server authentication system overview</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats?.total_keys || 0}</div>
          <div className="stat-label">
            <Key size={16} style={{ marginRight: '8px' }} />
            Total SSH Keys
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats?.active_keys || 0}</div>
          <div className="stat-label">
            <Activity size={16} style={{ marginRight: '8px' }} />
            Active Keys
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats?.total_servers || 0}</div>
          <div className="stat-label">
            <Server size={16} style={{ marginRight: '8px' }} />
            Total Servers
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats?.connected_servers || 0}</div>
          <div className="stat-label">
            <Activity size={16} style={{ marginRight: '8px' }} />
            Connected Servers
          </div>
        </div>
      </div>

      <div className="content-card">
        <div className="card-header">
          <h2 className="card-title">System Health</h2>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="active" fill="#34a853" name="Active" />
            <Bar dataKey="total" fill="#dadce0" name="Total" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="content-card">
        <div className="card-header">
          <h2 className="card-title">Recent Activity</h2>
        </div>
        <div className="recent-activity">
          {stats?.recent_activity?.length > 0 ? (
            stats.recent_activity.map((activity, index) => (
              <div key={index} className="activity-item" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 0',
                borderBottom: '1px solid #e8eaed'
              }}>
                <div>
                  <strong>{activity.action}</strong>
                  <p style={{ color: '#5f6368', fontSize: '14px', margin: '4px 0 0' }}>
                    {activity.details}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className={`status-badge status-${activity.status}`}>
                    {activity.status}
                  </span>
                  <p style={{ color: '#5f6368', fontSize: '12px', margin: '4px 0 0' }}>
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p style={{ textAlign: 'center', color: '#5f6368', padding: '20px' }}>
              No recent activity
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
