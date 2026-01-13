import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Card, CardContent } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { testAPI } from '../../services/api';
import PeopleIcon from '@mui/icons-material/People';
import GroupsIcon from '@mui/icons-material/Groups';
import SecurityIcon from '@mui/icons-material/Security';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

function Dashboard() {
  const [stats, setStats] = useState({ users: 0, teams: 0, permissions: 0 });
  const [testData, setTestData] = useState([]);

  useEffect(() => {
    loadStats();
    loadTestData();
    const interval = setInterval(() => {
      loadStats();
      loadTestData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const response = await testAPI.getStatus();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadTestData = () => {
    const mockData = [
      { name: 'User Lifecycle', passed: 45, failed: 2 },
      { name: 'Team Hierarchy', passed: 38, failed: 1 },
      { name: 'Permissions', passed: 52, failed: 3 },
      { name: 'Concurrent Ops', passed: 41, failed: 4 },
      { name: 'Security', passed: 48, failed: 1 },
    ];
    setTestData(mockData);
  };

  const StatCard = ({ title, value, icon, color }) => (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: color, opacity: 0.7 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Integration Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats.users}
            icon={<PeopleIcon sx={{ fontSize: 50 }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Teams"
            value={stats.teams}
            icon={<GroupsIcon sx={{ fontSize: 50 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Permissions"
            value={stats.permissions}
            icon={<SecurityIcon sx={{ fontSize: 50 }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Tests Passing"
            value="95%"
            icon={<CheckCircleIcon sx={{ fontSize: 50 }} />}
            color="#2e7d32"
          />
        </Grid>

        <Grid item xs={12} md={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Integration Test Results
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={testData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="passed" fill="#4caf50" name="Passed" />
                <Bar dataKey="failed" fill="#f44336" name="Failed" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Overview
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" paragraph>
                • User management system with complete lifecycle support
              </Typography>
              <Typography variant="body1" paragraph>
                • Team hierarchy with inherited permissions
              </Typography>
              <Typography variant="body1" paragraph>
                • Real-time permission validation and caching
              </Typography>
              <Typography variant="body1" paragraph>
                • Comprehensive audit logging for compliance
              </Typography>
              <Typography variant="body1">
                • Integration tests covering 5 critical scenarios
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
