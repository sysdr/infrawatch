import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Grid, Card, CardContent, CircularProgress
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getTeamDashboard, connectTeamWebSocket } from '../../services/api';

function TeamDashboard({ teamId }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [realtimeEvents, setRealtimeEvents] = useState([]);

  useEffect(() => {
    loadDashboard();
    
    const ws = connectTeamWebSocket(teamId, (event) => {
      setRealtimeEvents(prev => [event, ...prev].slice(0, 5));
      // Reload dashboard when member is added
      if (event.type === 'member_added') {
        setTimeout(() => loadDashboard(), 500);
      }
    });

    // Refresh dashboard every 10 seconds to get updated member count
    const interval = setInterval(() => {
      loadDashboard();
    }, 10000);

    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, [teamId]);

  const loadDashboard = async () => {
    try {
      const data = await getTeamDashboard(teamId);
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (!metrics) return <Typography>No data available</Typography>;

  const chartData = Object.entries(metrics.member_activity_distribution || {}).map(([userId, count]) => ({
    name: `User ${userId}`,
    activities: count
  }));

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Team Dashboard: {metrics.team_name}</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Members</Typography>
              <Typography variant="h4">{metrics.total_members}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Active Today</Typography>
              <Typography variant="h4">{metrics.active_members_today}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Active This Week</Typography>
              <Typography variant="h4">{metrics.active_members_week}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Activities</Typography>
              <Typography variant="h4">{metrics.total_activities}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Member Activity Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="activities" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 300, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>Real-time Events</Typography>
            {realtimeEvents.length > 0 ? (
              realtimeEvents.map((event, idx) => (
                <Box key={idx} sx={{ mb: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                  <Typography variant="body2" color="primary">{event.type}</Typography>
                  <Typography variant="caption">{event.message || event.content}</Typography>
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">No real-time events yet</Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Recent Activities</Typography>
            {metrics.recent_activities && metrics.recent_activities.length > 0 ? (
              <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                {metrics.recent_activities.map((activity, idx) => (
                  <Box 
                    key={activity.id || idx} 
                    sx={{ 
                      mb: 1.5, 
                      p: 1.5, 
                      bgcolor: 'background.paper',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
                      <Typography variant="body2" fontWeight="bold" color="primary">
                        {activity.type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {new Date(activity.created_at).toLocaleString()}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                      User ID: {activity.user_id}
                    </Typography>
                    <Typography variant="body2">
                      {activity.description}
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="textSecondary">No recent activities</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default TeamDashboard;
