import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { format } from 'date-fns';

const MetricsChart = ({ metrics = [] }) => {
  const chartData = useMemo(() => {
    // Group metrics by name and timestamp
    const grouped = metrics.reduce((acc, metric) => {
      const timestamp = new Date(metric.timestamp).getTime();
      const key = timestamp;
      
      if (!acc[key]) {
        acc[key] = {
          timestamp,
          time: format(new Date(timestamp), 'HH:mm:ss')
        };
      }
      
      acc[key][metric.name] = metric.value;
      return acc;
    }, {});

    return Object.values(grouped).sort((a, b) => a.timestamp - b.timestamp);
  }, [metrics]);

  const metricNames = useMemo(() => {
    const names = new Set();
    metrics.forEach(metric => names.add(metric.name));
    return Array.from(names);
  }, [metrics]);

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#ff00ff'];

  if (metrics.length === 0) {
    return (
      <div className="chart-empty">
        <p>No historical data available</p>
      </div>
    );
  }

  return (
    <div className="metrics-chart">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip 
            labelFormatter={(label) => `Time: ${label}`}
            formatter={(value, name) => [value, name]}
          />
          <Legend />
          {metricNames.map((name, index) => (
            <Line
              key={name}
              type="monotone"
              dataKey={name}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={false}
              connectNulls={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsChart;
