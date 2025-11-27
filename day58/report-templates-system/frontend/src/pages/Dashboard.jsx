import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, Card, CardContent } from '@mui/material';
import { Assessment, Schedule, CheckCircle, Error } from '@mui/icons-material';
import { reportApi } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalSchedules: 0,
    activeSchedules: 0,
    completedReports: 0,
    failedReports: 0
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [schedules, executions] = await Promise.all([
        reportApi.getSchedules(),
        reportApi.getExecutions()
      ]);

      const completed = executions.data.filter(e => e.status === 'completed').length;
      const failed = executions.data.filter(e => e.status === 'failed').length;

      setStats({
        totalSchedules: schedules.data.length,
        activeSchedules: schedules.data.length,
        completedReports: completed,
        failedReports: failed
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Schedules"
            value={stats.totalSchedules}
            icon={<Schedule sx={{ fontSize: 40 }} />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Schedules"
            value={stats.activeSchedules}
            icon={<Assessment sx={{ fontSize: 40 }} />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed Reports"
            value={stats.completedReports}
            icon={<CheckCircle sx={{ fontSize: 40 }} />}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Failed Reports"
            value={stats.failedReports}
            icon={<Error sx={{ fontSize: 40 }} />}
            color="error.main"
          />
        </Grid>
      </Grid>
    </Box>
  );
}
