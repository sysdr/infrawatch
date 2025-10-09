import React from 'react';
import { useQuery } from 'react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const COLORS = ['#0073aa', '#46b450', '#dc3232', '#f56e28', '#ffb900'];

const AlertStatistics = () => {
  const { data: stats, isLoading } = useQuery(
    'detailed-stats',
    async () => {
      const response = await axios.get('/api/alerts/statistics');
      return response.data;
    },
    { refetchInterval: 60000 }
  );

  if (isLoading) {
    return <div className="loading">Loading statistics...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Alert Statistics</h1>
        <p className="page-subtitle">Comprehensive alert analytics and trends</p>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px'}}>
        {/* Status Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Status Distribution</h3>
          </div>
          <div className="card-body">
            <PieChart width={300} height={200}>
              <Pie
                data={stats?.status_distribution || []}
                cx={150}
                cy={100}
                outerRadius={60}
                fill="#8884d8"
                dataKey="count"
                label={({status, count}) => `${status}: ${count}`}
              >
                {(stats?.status_distribution || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Severity Distribution</h3>
          </div>
          <div className="card-body">
            <BarChart width={300} height={200} data={stats?.severity_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="severity" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0073aa" />
            </BarChart>
          </div>
        </div>

        {/* Top Sources */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Top Alert Sources</h3>
          </div>
          <div className="card-body">
            <BarChart width={300} height={200} data={stats?.top_sources || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="source" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#46b450" />
            </BarChart>
          </div>
        </div>

        {/* Hourly Trend */}
        <div className="card" style={{gridColumn: 'span 2'}}>
          <div className="card-header">
            <h3 className="card-title">Alert Trend (Last 24 Hours)</h3>
          </div>
          <div className="card-body">
            <LineChart width={600} height={200} data={stats?.hourly_trend || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="hour" 
                tickFormatter={(value) => new Date(value).toLocaleTimeString([], {hour: '2-digit'})}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleString()}
              />
              <Line type="monotone" dataKey="count" stroke="#0073aa" strokeWidth={2} />
            </LineChart>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Summary</h3>
          </div>
          <div className="card-body">
            <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
              <div>
                <strong>Total Alerts:</strong>
                <span style={{fontSize: '24px', marginLeft: '10px', color: '#0073aa'}}>
                  {stats?.total_alerts || 0}
                </span>
              </div>
              <div>
                <strong>Active Alerts:</strong>
                <span style={{fontSize: '24px', marginLeft: '10px', color: '#dc3232'}}>
                  {stats?.active_alerts || 0}
                </span>
              </div>
              <div>
                <strong>Resolution Rate:</strong>
                <span style={{fontSize: '18px', marginLeft: '10px', color: '#46b450'}}>
                  {stats?.total_alerts ? 
                    Math.round(((stats.total_alerts - stats.active_alerts) / stats.total_alerts) * 100) : 0}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertStatistics;
