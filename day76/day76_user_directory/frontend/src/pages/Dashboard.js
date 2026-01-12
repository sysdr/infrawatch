import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Card, CardContent } from '@mui/material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import PeopleIcon from '@mui/icons-material/People';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import BlockIcon from '@mui/icons-material/Block';
import axios from 'axios';

const COLORS = ['#4caf50', '#ff9800', '#f44336', '#9e9e9e'];

function Dashboard() {
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    pending_users: 0,
    suspended_users: 0,
    ldap_synced_users: 0,
    provisioning_breakdown: { manual: 0, ldap_sync: 0, sso_jit: 0 }
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/stats/overview');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const statusData = [
    { name: 'Active', value: stats.active_users },
    { name: 'Pending', value: stats.pending_users },
    { name: 'Suspended', value: stats.suspended_users },
  ];

  const provisioningData = [
    { name: 'Manual', value: stats.provisioning_breakdown.manual },
    { name: 'LDAP Sync', value: stats.provisioning_breakdown.ldap_sync },
    { name: 'SSO JIT', value: stats.provisioning_breakdown.sso_jit },
  ];

  const StatCard = ({ title, value, icon, color }) => (
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard Overview</Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Total Users" 
            value={stats.total_users} 
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Active Users" 
            value={stats.active_users} 
            icon={<CheckCircleIcon sx={{ fontSize: 40 }} />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Pending" 
            value={stats.pending_users} 
            icon={<HourglassEmptyIcon sx={{ fontSize: 40 }} />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Suspended" 
            value={stats.suspended_users} 
            icon={<BlockIcon sx={{ fontSize: 40 }} />}
            color="#f44336"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>User Status Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Provisioning Methods</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={provisioningData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>LDAP Sync Status</Typography>
        <Typography variant="body1">
          LDAP Synced Users: <strong>{stats.ldap_synced_users}</strong> / {stats.total_users}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {stats.ldap_synced_users > 0 
            ? `${((stats.ldap_synced_users / stats.total_users) * 100).toFixed(1)}% of users synced with LDAP`
            : 'No LDAP synced users yet'
          }
        </Typography>
      </Paper>
    </Box>
  );
}

export default Dashboard;
