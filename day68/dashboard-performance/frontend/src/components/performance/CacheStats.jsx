import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { dashboardAPI } from '../../services/api';

function CacheStats() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const data = await dashboardAPI.getCacheStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading cache stats:', error);
    }
  };

  if (!stats) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Cache Performance</Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">Hit Rate</Typography>
          <Typography variant="h4" color="primary">{stats.hit_rate}%</Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label={`Hits: ${stats.hits}`} size="small" color="success" />
          <Chip label={`Misses: ${stats.misses}`} size="small" color="error" />
          <Chip label={`Keys: ${stats.total_keys}`} size="small" />
        </Box>
      </CardContent>
    </Card>
  );
}

export default CacheStats;
