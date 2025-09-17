import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, Zap, AlertTriangle, Users } from 'lucide-react';
import './Metrics.css';

const Metrics = ({ metrics = {}, detailed = false }) => {
  const sampleData = [
    { time: '00:00', throughput: 120, latency: 85, errors: 2 },
    { time: '04:00', throughput: 95, latency: 92, errors: 1 },
    { time: '08:00', throughput: 180, latency: 78, errors: 3 },
    { time: '12:00', throughput: 165, latency: 88, errors: 4 },
    { time: '16:00', throughput: 145, latency: 82, errors: 2 },
    { time: '20:00', throughput: 135, latency: 90, errors: 1 },
  ];

  const MetricCard = ({ icon: Icon, title, value, unit, trend, color }) => (
    <div className="metric-card">
      <div className="metric-header">
        <Icon className="metric-icon" style={{ color }} />
        <span className="metric-title">{title}</span>
      </div>
      <div className="metric-value">
        {value} <span className="metric-unit">{unit}</span>
      </div>
      {trend && (
        <div className={`metric-trend ${trend > 0 ? 'positive' : 'negative'}`}>
          {trend > 0 ? '+' : ''}{trend}%
        </div>
      )}
    </div>
  );

  if (!detailed) {
    return (
      <div className="metrics-overview">
        <h2>System Metrics</h2>
        <div className="metrics-grid">
          <MetricCard
            icon={TrendingUp}
            title="Throughput"
            value={metrics.throughput?.current || 0}
            unit="tasks/min"
            trend={5.2}
            color="#22c55e"
          />
          <MetricCard
            icon={Zap}
            title="Avg Latency"
            value={metrics.latency?.p50 || 0}
            unit="ms"
            trend={-2.1}
            color="#3b82f6"
          />
          <MetricCard
            icon={AlertTriangle}
            title="Error Rate"
            value={metrics.errors?.rate || 0}
            unit="%"
            trend={-0.5}
            color="#ef4444"
          />
          <MetricCard
            icon={Users}
            title="Active Workers"
            value={metrics.workers?.active || 0}
            unit="nodes"
            trend={8.3}
            color="#8b5cf6"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="metrics-detailed">
      <h2>Performance Metrics</h2>
      
      <div className="metrics-grid">
        <MetricCard
          icon={TrendingUp}
          title="Throughput"
          value={metrics.throughput?.current || 0}
          unit="tasks/min"
          trend={5.2}
          color="#22c55e"
        />
        <MetricCard
          icon={Zap}
          title="Avg Latency"
          value={metrics.latency?.p50 || 0}
          unit="ms"
          trend={-2.1}
          color="#3b82f6"
        />
        <MetricCard
          icon={AlertTriangle}
          title="Error Rate"
          value={metrics.errors?.rate || 0}
          unit="%"
          trend={-0.5}
          color="#ef4444"
        />
        <MetricCard
          icon={Users}
          title="Active Workers"
          value={metrics.workers?.active || 0}
          unit="nodes"
          trend={8.3}
          color="#8b5cf6"
        />
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Throughput Over Time</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={sampleData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Line type="monotone" dataKey="throughput" stroke="#22c55e" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Response Latency</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={sampleData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Line type="monotone" dataKey="latency" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Error Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={sampleData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Bar dataKey="errors" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Metrics;
