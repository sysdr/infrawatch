import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Button, Box,
  LinearProgress, Chip
} from '@mui/material';
import {
  Cloud as CloudIcon,
  Storage as StorageIcon,
  Timeline as TimelineIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { triggerScan, fetchChangeStats } from '../services/api';

function StatCard({ title, value, icon, color }) {
  return (
    <Card sx={{ height: '100%', bgcolor: color, color: 'white' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h4" fontWeight="bold">{value}</Typography>
            <Typography variant="body2">{title}</Typography>
          </Box>
          {icon}
        </Box>
      </CardContent>
    </Card>
  );
}

function DiscoveryDashboard({ stats }) {
  const [scanning, setScanning] = useState(false);
  const [changeStats, setChangeStats] = useState(null);

  useEffect(() => {
    loadChangeStats();
  }, []);

  const loadChangeStats = async () => {
    const data = await fetchChangeStats();
    setChangeStats(data);
  };

  const handleScan = async () => {
    setScanning(true);
    await triggerScan();
    setTimeout(() => setScanning(false), 3000);
  };

  const chartData = stats ? Object.entries(stats.by_type || {}).map(([name, value]) => ({
    name: name.replace('_', ' '),
    count: value
  })) : [];

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="bold">
          Infrastructure Overview
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={handleScan}
          disabled={scanning}
        >
          {scanning ? 'Scanning...' : 'Trigger Scan'}
        </Button>
      </Box>

      {scanning && <LinearProgress sx={{ mb: 2 }} />}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Total Resources"
            value={stats?.total_resources || 0}
            icon={<CloudIcon sx={{ fontSize: 48 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Resource Types"
            value={Object.keys(stats?.by_type || {}).length}
            icon={<StorageIcon sx={{ fontSize: 48 }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Changes (24h)"
            value={changeStats?.hourly_rate || 0}
            icon={<TimelineIcon sx={{ fontSize: 48 }} />}
            color="#ed6c02"
          />
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>Resources by Type</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>System Status</Typography>
              <Box display="flex" gap={1}>
                <Chip label="Discovery: Active" color="success" />
                <Chip label="Change Detection: Active" color="success" />
                <Chip label="Topology Mapping: Active" color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DiscoveryDashboard;
