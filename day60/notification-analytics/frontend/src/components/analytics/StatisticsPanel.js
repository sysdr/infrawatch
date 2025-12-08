import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Select, MenuItem, FormControl, InputLabel, Card, CardContent } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

function StatisticsPanel({ metrics, selectedMetric, onMetricChange }) {
  const [stats, setStats] = useState(null);
  const [windowSize, setWindowSize] = useState(3600);

  useEffect(() => {
    fetchStatistics();
    const interval = setInterval(fetchStatistics, 30000);
    return () => clearInterval(interval);
  }, [selectedMetric, windowSize]);

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/statistics/${selectedMetric}?window_size=${windowSize}`);
      setStats(response.data.statistics);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const StatCard = ({ title, value, unit = '' }) => (
    <Card elevation={2} sx={{ 
      height: '100%', 
      background: 'linear-gradient(135deg, #1f2937 0%, #374151 100%)', 
      color: 'white',
      borderRadius: 2,
      border: '1px solid #374151',
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: 4
      }
    }}>
      <CardContent>
        <Typography color="inherit" gutterBottom variant="body2" sx={{ opacity: 0.85, fontWeight: 500 }}>
          {title}
        </Typography>
        <Typography variant="h5" component="div" sx={{ fontWeight: 700, color: '#10b981' }}>
          {value !== null && value !== undefined ? value.toFixed(2) : '--'}
          <Typography component="span" variant="caption" sx={{ ml: 1, opacity: 0.7, color: 'inherit' }}>{unit}</Typography>
        </Typography>
      </CardContent>
    </Card>
  );

  if (!stats) return <Typography>Loading statistics...</Typography>;

  const chartData = [
    { name: 'Min', value: stats.min },
    { name: 'Mean', value: stats.mean },
    { name: 'Median', value: stats.median },
    { name: 'P95', value: stats.p95 },
    { name: 'P99', value: stats.p99 },
    { name: 'Max', value: stats.max }
  ];

  return (
    <Box>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel sx={{ color: '#6b7280' }}>Metric</InputLabel>
            <Select 
              value={selectedMetric} 
              onChange={(e) => onMetricChange(e.target.value)} 
              label="Metric"
              sx={{
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#e5e7eb'
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#d1d5db'
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#059669'
                }
              }}
            >
              {metrics.map(m => <MenuItem key={m} value={m}>{m}</MenuItem>)}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel sx={{ color: '#6b7280' }}>Time Window</InputLabel>
            <Select 
              value={windowSize} 
              onChange={(e) => setWindowSize(e.target.value)} 
              label="Time Window"
              sx={{
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#e5e7eb'
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#d1d5db'
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#059669'
                }
              }}
            >
              <MenuItem value={3600}>Last Hour</MenuItem>
              <MenuItem value={86400}>Last Day</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}><StatCard title="Mean" value={stats.mean} /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Median" value={stats.median} /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Std Dev" value={stats.std_dev} /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Count" value={stats.count} unit="samples" /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Min" value={stats.min} /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Max" value={stats.max} /></Grid>
        <Grid item xs={6} md={3}><StatCard title="P95" value={stats.p95} /></Grid>
        <Grid item xs={6} md={3}><StatCard title="P99" value={stats.p99} /></Grid>
      </Grid>

      <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid #e5e7eb' }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1f2937', fontWeight: 600 }}>Distribution Overview</Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: 8
              }} 
            />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#059669" strokeWidth={3} dot={{ fill: '#10b981', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  );
}

export default StatisticsPanel;
