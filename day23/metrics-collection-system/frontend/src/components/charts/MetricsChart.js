import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import styled from 'styled-components';
import { format } from 'date-fns';

const ChartContainer = styled.div`
  height: 300px;
`;

const ChartTitle = styled.h3`
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 1rem;
`;

const MetricsChart = ({ metrics }) => {
  const chartData = useMemo(() => {
    if (!metrics || metrics.length === 0) return [];
    
    // Group metrics by timestamp and calculate averages
    const grouped = metrics.reduce((acc, metric) => {
      const timestamp = Math.floor(metric.timestamp / 60) * 60; // Round to minute
      const key = format(new Date(timestamp * 1000), 'HH:mm');
      
      if (!acc[key]) {
        acc[key] = { time: key, values: [], count: 0 };
      }
      
      if (metric.data && typeof metric.data.value === 'number') {
        acc[key].values.push(metric.data.value);
        acc[key].count++;
      }
      
      return acc;
    }, {});
    
    // Calculate averages and return sorted data
    return Object.values(grouped)
      .map(group => ({
        time: group.time,
        value: group.values.length > 0 
          ? group.values.reduce((sum, val) => sum + val, 0) / group.values.length 
          : 0,
        count: group.count
      }))
      .sort((a, b) => a.time.localeCompare(b.time))
      .slice(-20); // Last 20 data points
  }, [metrics]);

  return (
    <div>
      <ChartTitle>Metrics Timeline</ChartTitle>
      <ChartContainer>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ecf0f1" />
            <XAxis 
              dataKey="time" 
              stroke="#7f8c8d"
              fontSize={12}
            />
            <YAxis 
              stroke="#7f8c8d"
              fontSize={12}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)'
              }}
              formatter={(value, name) => [
                `${value.toFixed(2)}${name === 'value' ? '' : ''}`, 
                'Average Value'
              ]}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#667eea" 
              strokeWidth={3}
              dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#667eea', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>
    </div>
  );
};

export default MetricsChart;
