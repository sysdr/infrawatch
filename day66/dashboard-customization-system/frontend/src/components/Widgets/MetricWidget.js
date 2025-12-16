import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

const MetricWidget = ({ config }) => {
  const [value, setValue] = useState(() => Math.random() * 1000 + 10); // Start with non-zero value
  const [trend, setTrend] = useState(0);

  useEffect(() => {
    const updateValue = () => {
      setValue(prevValue => {
        const newValue = Math.random() * 1000 + 10; // Ensure non-zero (min 10)
        setTrend(newValue - prevValue);
        return newValue;
      });
    };

    // Update immediately on mount
    updateValue();
    
    // Set up interval for periodic updates
    const interval = setInterval(updateValue, config.refreshInterval || 5000); // Default 5 seconds for demo
    return () => clearInterval(interval);
  }, [config.refreshInterval]);

  return (
    <Paper sx={{ p: 3, height: '100%', bgcolor: 'var(--paper)', textAlign: 'center' }}>
      <Typography variant="subtitle1" color="textSecondary">
        {config.title || 'Metric'}
      </Typography>
      <Typography variant="h3" sx={{ my: 2, color: 'var(--text)' }}>
        {value.toFixed(2)}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {trend >= 0 ? (
          <TrendingUpIcon sx={{ color: 'green', mr: 1 }} />
        ) : (
          <TrendingDownIcon sx={{ color: 'red', mr: 1 }} />
        )}
        <Typography variant="body2" sx={{ color: trend >= 0 ? 'green' : 'red' }}>
          {Math.abs(trend).toFixed(2)}
        </Typography>
      </Box>
    </Paper>
  );
};

export default MetricWidget;
