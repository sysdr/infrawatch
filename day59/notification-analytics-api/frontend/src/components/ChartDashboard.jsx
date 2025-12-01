import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Paper, Grid, Typography, Box, Select, MenuItem, FormControl,
  InputLabel, CircularProgress, Alert
} from '@mui/material';
import { analyticsApi } from '../api/analyticsClient';
import { format } from 'date-fns';

function ChartDashboard() {
  const [metric, setMetric] = useState('event_count');
  const [timeRange, setTimeRange] = useState(24);

  const { data, isLoading, error } = useQuery({
    queryKey: ['timeseries', metric, timeRange],
    queryFn: () => analyticsApi.getTimeseriesData(metric, 'email,sms,push', timeRange),
    refetchInterval: 30000, // Refetch every 30s
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading chart data: {error.message}</Alert>;
  }

  const chartData = data?.data?.map(d => ({
    ...d,
    time: format(new Date(d.time), 'HH:mm')
  })) || [];

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">Notification Metrics Over Time</Typography>
              <Box display="flex" gap={2}>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Metric</InputLabel>
                  <Select value={metric} onChange={(e) => setMetric(e.target.value)} label="Metric">
                    <MenuItem value="event_count">Event Count</MenuItem>
                    <MenuItem value="delivery_rate">Delivery Rate</MenuItem>
                    <MenuItem value="avg_processing_time">Avg Processing Time</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Time Range</InputLabel>
                  <Select value={timeRange} onChange={(e) => setTimeRange(e.target.value)} label="Time Range">
                    <MenuItem value={6}>6 Hours</MenuItem>
                    <MenuItem value={24}>24 Hours</MenuItem>
                    <MenuItem value={168}>7 Days</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
            
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="time" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #ccc',
                    borderRadius: '4px'
                  }} 
                />
                <Legend />
                <Line type="monotone" dataKey="email" stroke="#2196f3" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="sms" stroke="#4caf50" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="push" stroke="#ff9800" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Channel Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData.slice(-24)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="time" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip />
                <Legend />
                <Bar dataKey="email" fill="#2196f3" />
                <Bar dataKey="sms" fill="#4caf50" />
                <Bar dataKey="push" fill="#ff9800" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Summary Statistics</Typography>
            <Grid container spacing={2}>
              {data?.channels?.map(channel => {
                const channelData = chartData.map(d => d[channel] || 0);
                const total = channelData.reduce((a, b) => a + b, 0);
                const avg = total / channelData.length || 0;
                
                return (
                  <Grid item xs={12} key={channel}>
                    <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        {channel.toUpperCase()}
                      </Typography>
                      <Typography variant="h5" sx={{ mt: 1 }}>
                        {avg.toFixed(2)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Average {metric.replace('_', ' ')}
                      </Typography>
                    </Box>
                  </Grid>
                );
              })}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ChartDashboard;
