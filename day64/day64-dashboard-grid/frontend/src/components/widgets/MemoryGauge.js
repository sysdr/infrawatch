import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, LinearProgress } from '@mui/material';

const MemoryGauge = ({ config = {} }) => {
  const [memoryUsage, setMemoryUsage] = useState(0);

  useEffect(() => {
    const updateMemory = () => {
      setMemoryUsage(Math.floor(Math.random() * 100));
    };

    const interval = setInterval(updateMemory, 3000);
    updateMemory();

    return () => clearInterval(interval);
  }, []);

  const threshold = config.threshold || 80;
  const color = memoryUsage > threshold ? 'error' : 'primary';

  return (
    <Paper sx={{ height: '100%', p: 2.5, display: 'flex', flexDirection: 'column', justifyContent: 'center', bgcolor: 'transparent', boxShadow: 'none' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1e293b' }}>
        Memory Usage
      </Typography>
      <Box sx={{ textAlign: 'center', my: 2 }}>
        <Typography 
          variant="h2" 
          sx={{ 
            color: memoryUsage > threshold ? '#ef4444' : '#10b981',
            fontWeight: 700,
          }}
        >
          {memoryUsage}%
        </Typography>
      </Box>
      <LinearProgress 
        variant="determinate" 
        value={memoryUsage} 
        sx={{ 
          height: 12, 
          borderRadius: 6,
          bgcolor: '#e2e8f0',
          '& .MuiLinearProgress-bar': {
            bgcolor: memoryUsage > threshold ? '#ef4444' : '#10b981',
            borderRadius: 6,
          },
        }} 
      />
      <Typography variant="caption" sx={{ mt: 1.5, textAlign: 'center', color: '#64748b' }}>
        Threshold: {threshold}%
      </Typography>
    </Paper>
  );
};

export default MemoryGauge;
