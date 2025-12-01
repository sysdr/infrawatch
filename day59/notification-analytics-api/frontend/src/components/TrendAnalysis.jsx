import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import {
  Paper, Grid, Typography, Box, Select, MenuItem, FormControl,
  InputLabel, Chip, Alert, CircularProgress
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import { analyticsApi } from '../api/analyticsClient';

function TrendAnalysis() {
  const [metric, setMetric] = useState('delivery_rate');
  const [channel, setChannel] = useState('email');
  const [days, setDays] = useState(7);

  const { data, isLoading, error } = useQuery({
    queryKey: ['trends', metric, channel, days],
    queryFn: () => analyticsApi.getTrends(metric, channel, days),
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading trend data: {error.message}</Alert>;
  }

  const getTrendIcon = (direction) => {
    if (direction === 'up') return <TrendingUpIcon />;
    if (direction === 'down') return <TrendingDownIcon />;
    return <TrendingFlatIcon />;
  };

  const getTrendColor = (direction) => {
    if (direction === 'up') return 'success';
    if (direction === 'down') return 'error';
    return 'default';
  };

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">Trend Analysis</Typography>
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
                  <InputLabel>Channel</InputLabel>
                  <Select value={channel} onChange={(e) => setChannel(e.target.value)} label="Channel">
                    <MenuItem value="email">Email</MenuItem>
                    <MenuItem value="sms">SMS</MenuItem>
                    <MenuItem value="push">Push</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 100 }}>
                  <InputLabel>Period</InputLabel>
                  <Select value={days} onChange={(e) => setDays(e.target.value)} label="Period">
                    <MenuItem value={7}>7 Days</MenuItem>
                    <MenuItem value={14}>14 Days</MenuItem>
                    <MenuItem value={30}>30 Days</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>

            <Grid container spacing={3} mb={3}>
              <Grid item xs={12} md={3}>
                <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Current Value
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }}>
                    {data?.current_value?.toFixed(2)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Change
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mt={1}>
                    <Typography variant="h4">
                      {Math.abs(data?.percent_change || 0).toFixed(1)}%
                    </Typography>
                    <Chip
                      icon={getTrendIcon(data?.direction)}
                      label={data?.direction}
                      color={getTrendColor(data?.direction)}
                      size="small"
                    />
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Trend
                  </Typography>
                  <Typography variant="h5" sx={{ mt: 1 }}>
                    {data?.trend}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Anomalies
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }} color={data?.anomalies?.length > 0 ? 'error' : 'inherit'}>
                    {data?.anomalies?.length || 0}
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            {data?.anomalies?.length > 0 && (
              <Alert severity="warning" sx={{ mb: 3 }}>
                Detected {data.anomalies.length} anomalies in the selected time period
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default TrendAnalysis;
