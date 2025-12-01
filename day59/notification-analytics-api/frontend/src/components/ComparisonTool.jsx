import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer
} from 'recharts';
import {
  Paper, Grid, Typography, Box, Select, MenuItem, FormControl,
  InputLabel, CircularProgress, Alert, Chip
} from '@mui/material';
import { analyticsApi } from '../api/analyticsClient';

function ComparisonTool() {
  const [metric, setMetric] = useState('delivery_rate');
  const [days, setDays] = useState(7);

  const { data, isLoading, error } = useQuery({
    queryKey: ['compare-channels', metric, days],
    queryFn: () => analyticsApi.compareChannels(metric, 'email,sms,push', days),
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading comparison data: {error.message}</Alert>;
  }

  const chartData = Object.entries(data?.comparisons || {}).map(([channel, stats]) => ({
    channel: channel.toUpperCase(),
    average: stats.average,
    total: stats.total,
  }));

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">Channel Comparison</Typography>
              <Box display="flex" gap={2}>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Metric</InputLabel>
                  <Select value={metric} onChange={(e) => setMetric(e.target.value)} label="Metric">
                    <MenuItem value="delivery_rate">Delivery Rate</MenuItem>
                    <MenuItem value="event_count">Event Count</MenuItem>
                    <MenuItem value="avg_processing_time">Processing Time</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Period</InputLabel>
                  <Select value={days} onChange={(e) => setDays(e.target.value)} label="Period">
                    <MenuItem value={7}>7 Days</MenuItem>
                    <MenuItem value={14}>14 Days</MenuItem>
                    <MenuItem value={30}>30 Days</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>

            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="channel" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip />
                <Legend />
                <Bar dataKey="average" fill="#2196f3" name="Average Value" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Detailed Comparison</Typography>
            <Grid container spacing={2}>
              {Object.entries(data?.comparisons || {}).map(([channel, stats]) => (
                <Grid item xs={12} md={4} key={channel}>
                  <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {channel.toUpperCase()}
                    </Typography>
                    <Box display="flex" flexDirection="column" gap={1}>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">Average:</Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {stats.average.toFixed(2)}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">Total:</Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {stats.total.toFixed(0)}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">Data Points:</Typography>
                        <Typography variant="body1">
                          {stats.data_points}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>

            {data?.summary && (
              <Box mt={3} p={2} sx={{ bgcolor: '#e3f2fd', borderRadius: 1 }}>
                <Typography variant="subtitle1" gutterBottom>Summary</Typography>
                <Box display="flex" gap={2} flexWrap="wrap">
                  <Chip label={`Best: ${data.summary.highest}`} color="success" />
                  <Chip label={`Worst: ${data.summary.lowest}`} color="error" />
                  <Chip label={`Difference: ${parseFloat(data.summary.percent_difference || 0).toFixed(1)}%`} />
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ComparisonTool;
