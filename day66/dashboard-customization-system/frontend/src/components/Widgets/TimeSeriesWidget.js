import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Paper, Typography, Box } from '@mui/material';

const TimeSeriesWidget = ({ config, theme }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Generate sample time series data with non-zero values
    const generateData = () => {
      const now = Date.now();
      return Array.from({ length: 20 }, (_, i) => ({
        time: now - (19 - i) * 60000,
        value: Math.random() * 100 + 5 // Ensure minimum value of 5
      }));
    };

    setData(generateData());
    const interval = setInterval(() => {
      setData(generateData());
    }, config.refreshInterval || 5000); // Default 5 seconds for demo

    return () => clearInterval(interval);
  }, [config.refreshInterval]);

  return (
    <Paper sx={{ p: 2, height: '100%', bgcolor: 'var(--paper)' }}>
      <Typography variant="h6" gutterBottom>{config.title || 'Time Series'}</Typography>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="time"
            tickFormatter={(time) => new Date(time).toLocaleTimeString()}
            stroke="var(--text)"
          />
          <YAxis stroke="var(--text)" />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--paper)',
              border: '1px solid var(--border)',
              color: 'var(--text)'
            }}
          />
          <Line type="monotone" dataKey="value" stroke="var(--primary)" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default TimeSeriesWidget;
