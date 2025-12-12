import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const MetricCard = ({ config = {} }) => {
  const [value, setValue] = useState(0);

  useEffect(() => {
    const updateValue = () => {
      setValue(Math.floor(Math.random() * 1000) + 500);
    };

    const interval = setInterval(updateValue, 2000);
    updateValue();

    return () => clearInterval(interval);
  }, []);

  return (
    <Paper sx={{ height: '100%', p: 2.5, display: 'flex', flexDirection: 'column', justifyContent: 'center', bgcolor: 'transparent', boxShadow: 'none' }}>
      <Typography 
        variant="subtitle2" 
        sx={{ 
          color: '#64748b',
          fontWeight: 500,
          mb: 1.5,
          textTransform: 'uppercase',
          fontSize: '0.75rem',
          letterSpacing: '0.5px',
        }}
      >
        {config.metric || 'Requests/Second'}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            fontWeight: 700,
            color: '#1e293b',
          }}
        >
          {value.toLocaleString()}
        </Typography>
        <TrendingUpIcon sx={{ color: '#10b981', fontSize: '2rem' }} />
      </Box>
    </Paper>
  );
};

export default MetricCard;
