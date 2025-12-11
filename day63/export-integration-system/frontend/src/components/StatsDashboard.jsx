import React, { useState, useEffect } from 'react';
import { Paper, Grid, Box, Typography } from '@mui/material';
import { CheckCircle, Error, Schedule, CloudQueue } from '@mui/icons-material';
import { exportAPI } from '../services/api';

const StatCard = ({ title, value, icon, color }) => (
    <Paper elevation={3} sx={{ p: 3, background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)` }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
                <Typography variant="h4" fontWeight="bold">{value}</Typography>
                <Typography variant="body2" color="text.secondary">{title}</Typography>
            </Box>
            <Box sx={{ color, fontSize: 48 }}>{icon}</Box>
        </Box>
    </Paper>
);

const StatsDashboard = () => {
    const [stats, setStats] = useState({
        total_jobs: 0,
        completed_jobs: 0,
        failed_jobs: 0,
        pending_jobs: 0,
        total_schedules: 0,
        active_schedules: 0
    });

    useEffect(() => {
        const loadStats = async () => {
            try {
                const response = await exportAPI.getStats();
                setStats(response.data);
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        };

        loadStats();
        const interval = setInterval(loadStats, 10000); // Poll every 10 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Total Jobs"
                    value={stats.total_jobs}
                    icon={<CloudQueue />}
                    color="#2196f3"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Completed"
                    value={stats.completed_jobs}
                    icon={<CheckCircle />}
                    color="#4caf50"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Failed"
                    value={stats.failed_jobs}
                    icon={<Error />}
                    color="#f44336"
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Active Schedules"
                    value={stats.active_schedules}
                    icon={<Schedule />}
                    color="#ff9800"
                />
            </Grid>
        </Grid>
    );
};

export default StatsDashboard;
