import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const RealtimeMetrics = ({ metrics = {}, limit }) => {
  const metricsArray = Object.entries(metrics).map(([key, value]) => ({
    key,
    ...value
  }));

  // Sort by timestamp and limit if specified
  const sortedMetrics = metricsArray
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, limit);

  if (sortedMetrics.length === 0) {
    return (
      <div className="realtime-empty">
        <p>No real-time data available</p>
        <small>Metrics will appear here as they are collected</small>
      </div>
    );
  }

  const getTrendIcon = (value) => {
    if (value > 50) return <TrendingUp className="trend-up" size={16} />;
    if (value < 50) return <TrendingDown className="trend-down" size={16} />;
    return <Minus className="trend-neutral" size={16} />;
  };

  return (
    <div className="realtime-metrics">
      {sortedMetrics.map((metric) => (
        <div key={metric.key} className="metric-item">
          <div className="metric-header">
            <div className="metric-name">{metric.name}</div>
            <div className="metric-value">
              {getTrendIcon(metric.value)}
              {metric.value.toFixed(2)}
            </div>
          </div>
          <div className="metric-details">
            <span className="metric-source">Source: {metric.source}</span>
            <span className="metric-time">
              {formatDistanceToNow(new Date(metric.timestamp), { addSuffix: true })}
            </span>
          </div>
          {metric.tags && (
            <div className="metric-tags">
              {Object.entries(metric.tags).map(([key, value]) => (
                <span key={key} className="tag">
                  {key}: {value}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default RealtimeMetrics;
